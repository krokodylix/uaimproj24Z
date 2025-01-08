package com.illusion.admin

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.example.agromobile.R
import com.illusion.network.ApiService
import com.illusion.utils.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ReportActivity : AppCompatActivity() {
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_report)

        sessionManager = SessionManager(this)

        val startDateInput = findViewById<EditText>(R.id.startDateInput)
        val endDateInput = findViewById<EditText>(R.id.endDateInput)
        val generateReportButton = findViewById<Button>(R.id.generateReportButton)
        val reportResultTextView = findViewById<TextView>(R.id.reportResultTextView)

        generateReportButton.setOnClickListener {
            val startDate = startDateInput.text.toString()
            val endDate = endDateInput.text.toString()

            if (startDate.isBlank() || endDate.isBlank()) {
                Toast.makeText(this, "Please enter valid dates", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val token = sessionManager.getToken()
            if (token != null) {
                ApiService.instance.generateReport("Bearer $token", startDate, endDate)
                    .enqueue(object : Callback<Map<String, Any>> {
                        override fun onResponse(call: Call<Map<String, Any>>, response: Response<Map<String, Any>>) {
                            if (response.isSuccessful) {
                                val report = response.body()
                                val totalOrders = report?.get("total_orders") ?: "N/A"
                                val totalSum = report?.get("total_sum") ?: "N/A"
                                val ordersPerProvince = report?.get("orders_per_province") ?: "N/A"

                                reportResultTextView.text = """
                                    Total Orders: $totalOrders
                                    Total Sum: $totalSum PLN
                                    Orders per Province: $ordersPerProvince
                                """.trimIndent()
                            } else {
                                Toast.makeText(this@ReportActivity, "Failed to generate report", Toast.LENGTH_SHORT).show()
                            }
                        }

                        override fun onFailure(call: Call<Map<String, Any>>, t: Throwable) {
                            Toast.makeText(this@ReportActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                        }
                    })
            }
        }
    }
}
