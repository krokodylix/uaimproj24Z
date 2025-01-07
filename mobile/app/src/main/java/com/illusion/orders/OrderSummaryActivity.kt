package com.illusion.orders

import android.os.Bundle
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.agromobile.R
import com.illusion.network.ApiService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.text.SimpleDateFormat
import java.util.*

class OrderSummaryActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_order_summary)

        val totalOrdersTextView = findViewById<TextView>(R.id.totalOrders)
        val totalSumTextView = findViewById<TextView>(R.id.totalSum)
        val ordersPerProvinceTextView = findViewById<TextView>(R.id.ordersPerProvince)

        // Generate default startDate and endDate (last 30 days)
        val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
        val calendar = Calendar.getInstance()
        val endDate = dateFormat.format(calendar.time)
        calendar.add(Calendar.DAY_OF_MONTH, -30)
        val startDate = dateFormat.format(calendar.time)

        // Fetch order summary data
        ApiService.instance.getOrderSummary(startDate, endDate).enqueue(object : Callback<OrderSummaryResponse> {
            override fun onResponse(call: Call<OrderSummaryResponse>, response: Response<OrderSummaryResponse>) {
                if (response.isSuccessful) {
                    val summary = response.body()
                    if (summary != null) {
                        totalOrdersTextView.text = "Total Orders: ${summary.totalOrders}"
                        totalSumTextView.text = "Total Sum: ${summary.totalSum} PLN"

                        val provinceSummary = summary.ordersPerProvince.map { (province, count) ->
                            "$province: $count orders"
                        }.joinToString("\n")
                        ordersPerProvinceTextView.text = provinceSummary
                    }
                } else {
                    Toast.makeText(this@OrderSummaryActivity, "Failed to fetch summary", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<OrderSummaryResponse>, t: Throwable) {
                Toast.makeText(this@OrderSummaryActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
