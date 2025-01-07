package com.illusion.orders

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
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class OrderActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_order)

        val productInput = findViewById<EditText>(R.id.productInput)
        val deliveryDateInput = findViewById<EditText>(R.id.deliveryDateInput)
        val addressInput = findViewById<EditText>(R.id.addressInput)
        val provinceSpinner = findViewById<Spinner>(R.id.provinceInput)
        val transportTypeSpinner = findViewById<Spinner>(R.id.transportTypeInput)
        val placeOrderButton = findViewById<Button>(R.id.placeOrderButton)

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
            val productId = productInput.text.toString().toIntOrNull()
            val deliveryDate = deliveryDateInput.text.toString()
            val address = addressInput.text.toString()
            val selectedProvince = provinceSpinner.selectedItem as String
            val selectedTransportType = transportTypeSpinner.selectedItem as String

            if (productId == null || deliveryDate.isBlank() || address.isBlank() || selectedProvince.isBlank() || selectedTransportType.isBlank()) {
                Toast.makeText(this, "All fields are required", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val orderMap = mapOf(
                "product_id" to productId,
                "delivery_date" to deliveryDate,
                "address" to address,
                "province" to selectedProvince,
                "transport_type" to selectedTransportType
            )

            ApiService.instance.createOrder(orderMap).enqueue(object : Callback<Void> {
                override fun onResponse(call: Call<Void>, response: Response<Void>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@OrderActivity, "Order placed successfully", Toast.LENGTH_SHORT).show()
                        finish()
                    } else {
                        Toast.makeText(this@OrderActivity, "Failed to place order", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<Void>, t: Throwable) {
                    Toast.makeText(this@OrderActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }
    }
}
