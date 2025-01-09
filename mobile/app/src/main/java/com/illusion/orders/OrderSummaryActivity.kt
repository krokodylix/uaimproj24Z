package com.illusion.orders

import android.content.Intent
import android.graphics.BitmapFactory
import android.os.Bundle
import android.util.Base64
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide
import com.example.agromobile.R
import com.illusion.products.ProductListActivity
import com.illusion.network.ApiService
import com.illusion.products.ProductDetailResponse
import com.illusion.utils.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response


class OrderSummaryActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_order_summary)

        val productImageView = findViewById<ImageView>(R.id.productImageView)
        val descriptionTextView = findViewById<TextView>(R.id.descriptionTextView)
        val orderIdTextView = findViewById<TextView>(R.id.orderIdTextView)
        val totalSumTextView = findViewById<TextView>(R.id.totalSumTextView)
        val deliveryDetailsTextView = findViewById<TextView>(R.id.deliveryDetailsTextView)
        val returnToListButton = findViewById<Button>(R.id.returnToListButton)

        val orderId = intent.getIntExtra("order_id", -1)
        if (orderId == -1) {
            Toast.makeText(this, "Invalid order ID", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        // Fetch order details
        val token = SessionManager(this).getToken()
        if (token != null) {
            ApiService.instance.getOrder("Bearer $token", orderId).enqueue(object : Callback<OrderSummaryResponse> {
                override fun onResponse(call: Call<OrderSummaryResponse>, response: Response<OrderSummaryResponse>) {
                    if (response.isSuccessful) {
                        val summary = response.body()
                        if (summary != null) {

                            if (summary != null) {
                                summary.image?.let {
                                    val imageBytes = Base64.decode(it, Base64.DEFAULT)
                                    val bitmap =
                                        BitmapFactory.decodeByteArray(
                                            imageBytes,
                                            0,
                                            imageBytes.size
                                        )
                                    productImageView.setImageBitmap(bitmap)
                                }
                            }


                            // Set order details
                            descriptionTextView.text = summary.product_description
                            orderIdTextView.text = "Id: ${summary.order_id}"
                            totalSumTextView.text = "Total Sum: ${summary.total_sum} PLN"
                            deliveryDetailsTextView.text =
                                "Delivery to ${summary.address} in ${summary.province} via ${summary.transport_type} on ${summary.delivery_date}"
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


        // Handle return to list button
        returnToListButton.setOnClickListener {
            val intent = Intent(this, ProductListActivity::class.java)
            startActivity(intent)
            finish()
        }
    }
}
