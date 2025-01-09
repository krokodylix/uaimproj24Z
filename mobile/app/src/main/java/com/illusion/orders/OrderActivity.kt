package com.illusion.orders

import android.app.DatePickerDialog
import android.content.Intent
import android.graphics.BitmapFactory
import android.os.Bundle
import android.util.Base64
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide
import com.example.agromobile.R
import com.illusion.network.ApiService
import com.illusion.network.Province
import com.illusion.network.TransportType
import com.illusion.products.ProductDetailResponse
import com.illusion.utils.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.text.SimpleDateFormat
import java.util.*

class OrderActivity : AppCompatActivity() {
    private lateinit var sessionManager: SessionManager
    private lateinit var productImageView: ImageView
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_order)

        sessionManager = SessionManager(this)

        productImageView = findViewById(R.id.productImageView)
        val productDescription = findViewById<TextView>(R.id.productDescription)
        val productIdText = findViewById<TextView>(R.id.productIdText)
        val productPriceText = findViewById<TextView>(R.id.productPriceText)
        val deliveryDateInput = findViewById<EditText>(R.id.deliveryDateInput)
        val addressInput = findViewById<EditText>(R.id.addressInput)
        val provinceSpinner = findViewById<Spinner>(R.id.provinceInput)
        val transportTypeSpinner = findViewById<Spinner>(R.id.transportTypeInput)
        val placeOrderButton = findViewById<Button>(R.id.placeOrderButton)

        // Get product ID from Intent
        val productId = intent.getIntExtra("product_id", -1)
        if (productId == -1) {
            Toast.makeText(this, "Invalid product ID", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        // Fetch product details
        ApiService.instance.getProductDetails(productId).enqueue(object : Callback<ProductDetailResponse> {
            override fun onResponse(call: Call<ProductDetailResponse>, response: Response<ProductDetailResponse>) {
                if (response.isSuccessful) {
                    val product = response.body()
                    if (product != null) {
                        product.image?.let {
                            val imageBytes = Base64.decode(it, Base64.DEFAULT)
                            val bitmap =
                                BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)
                            productImageView.setImageBitmap(bitmap)
                        }

                        productDescription.text = product.description
                        productIdText.text = "Id: ${product.id}"
                        productPriceText.text = "Price: ${product.price} PLN"
                    }
                } else {
                    Toast.makeText(this@OrderActivity, "Failed to load product details", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<ProductDetailResponse>, t: Throwable) {
                Toast.makeText(this@OrderActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })

        // Populate Province Spinner
        val provinceAdapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_item,
            Province.values().map { it.value }
        )
        provinceAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        provinceSpinner.adapter = provinceAdapter

        // Populate TransportType Spinner
        val transportTypeAdapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_item,
            TransportType.values().map { it.value }
        )
        transportTypeAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        transportTypeSpinner.adapter = transportTypeAdapter

        // Date Picker for Delivery Date
        deliveryDateInput.setOnClickListener {
            showFutureDatePicker { date -> deliveryDateInput.setText(date) }
        }

        placeOrderButton.setOnClickListener {
            val deliveryDate = deliveryDateInput.text.toString()
            val address = addressInput.text.toString()
            val selectedProvince = provinceSpinner.selectedItem as String
            val selectedTransportType = transportTypeSpinner.selectedItem as String

            if (deliveryDate.isBlank() || address.isBlank() || selectedProvince.isBlank() || selectedTransportType.isBlank()) {
                Toast.makeText(this, "All fields are required", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val orderMap = mapOf(
                "product_id" to productId.toString(),
                "delivery_date" to deliveryDate,
                "address" to address,
                "province" to selectedProvince,
                "transport_type" to selectedTransportType
            )

            ApiService.instance.createOrder("Bearer ${sessionManager.getToken()}", orderMap).enqueue(object : Callback<Map<String, Any>> {
                override fun onResponse(call: Call<Map<String, Any>>, response: Response<Map<String, Any>>) {
                    if (response.isSuccessful) {
                        val responseBody = response.body()
                        val orderId = (responseBody?.get("order_id") as? Double)?.toInt()
                        if (orderId != null) {
                            val intent = Intent(this@OrderActivity, OrderSummaryActivity::class.java)
                            intent.putExtra("order_id", orderId)
                            startActivity(intent)
                        } else {
                            Toast.makeText(this@OrderActivity, "Failed to retrieve order summary", Toast.LENGTH_SHORT).show()
                        }
                        finish()
                    } else {
                        Toast.makeText(this@OrderActivity, "Failed to place order", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<Map<String, Any>>, t: Throwable) {
                    Toast.makeText(this@OrderActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }
    }

    private fun showFutureDatePicker(onDateSelected: (String) -> Unit) {
        val calendar = Calendar.getInstance()
        calendar.add(Calendar.DAY_OF_YEAR, 3) // Ensure the date is at least 3 days out

        val datePickerDialog = DatePickerDialog(
            this,
            { _, year, month, day ->
                val selectedDate = Calendar.getInstance()
                selectedDate.set(year, month, day)

                // Format the selected date
                onDateSelected(dateFormat.format(selectedDate.time))
            },
            calendar.get(Calendar.YEAR),
            calendar.get(Calendar.MONTH),
            calendar.get(Calendar.DAY_OF_MONTH)
        )

        datePickerDialog.datePicker.minDate = calendar.timeInMillis

        datePickerDialog.show()
    }
}
