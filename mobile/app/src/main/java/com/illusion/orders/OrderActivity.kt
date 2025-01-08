package com.illusion.orders

import android.content.Intent
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.agromobile.R
import com.illusion.network.ApiService
import com.illusion.network.Province
import com.illusion.network.TransportType
import com.illusion.utils.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class OrderActivity : AppCompatActivity() {
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_order)

        sessionManager = SessionManager(this)

        val productInput = findViewById<EditText>(R.id.productInput)
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

        // Display product ID (non-editable)
        productInput.setText(productId.toString())
        productInput.isEnabled = false

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
}
