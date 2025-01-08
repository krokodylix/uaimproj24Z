package com.illusion.orders

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.agromobile.R
import com.illusion.products.ProductListActivity
import com.illusion.network.ApiService
import com.illusion.utils.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class OrderSummaryActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_order_summary)

        val orderIdTextView = findViewById<TextView>(R.id.totalOrders)
        val totalSumTextView = findViewById<TextView>(R.id.totalSum)
        val provinceTextView = findViewById<TextView>(R.id.ordersPerProvince)
        val returnToListButton = findViewById<Button>(R.id.returnToListButton)

        val orderId = intent.getIntExtra("order_id", -1)
        if (orderId == -1) {
            Toast.makeText(this, "Invalid order ID", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        // Fetch order details
        ApiService.instance.getOrder("Bearer ${SessionManager(this).getToken()}", orderId).enqueue(object : Callback<OrderSummaryResponse> {
            override fun onResponse(call: Call<OrderSummaryResponse>, response: Response<OrderSummaryResponse>) {
                if (response.isSuccessful) {
                    val summary = response.body()
                    if (summary != null) {
                        orderIdTextView.text = "Order ID: ${summary.order_id}"
                        totalSumTextView.text = "Total Sum: ${summary.total_sum} PLN"
                        provinceTextView.text = "Delivery to: ${summary.province}"
                    }
                } else {
                    Toast.makeText(this@OrderSummaryActivity, "Failed to fetch summary", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<OrderSummaryResponse>, t: Throwable) {
                Toast.makeText(this@OrderSummaryActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })

        // Handle return to list button
        returnToListButton.setOnClickListener {
            val intent = Intent(this, ProductListActivity::class.java)
            startActivity(intent)
            finish()
        }
    }
}
