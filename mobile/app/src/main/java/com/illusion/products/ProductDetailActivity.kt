package com.illusion.products

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide
import com.example.agromobile.R
import com.illusion.orders.OrderActivity
import com.illusion.network.ApiService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ProductDetailActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_detail)

        val productId = intent.getIntExtra("product_id", -1)
        val productImageView = findViewById<ImageView>(R.id.productImageView)
        val productDescriptionView = findViewById<TextView>(R.id.productDescriptionView)
        val productPriceView = findViewById<TextView>(R.id.productPriceView)
        val orderButton = findViewById<Button>(R.id.orderButton)

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
                        productDescriptionView.text = product.description
                        productPriceView.text = "Price: ${product.price} PLN"

                        // Load image using Glide (if image is available)
                        if (!product.image.isNullOrEmpty()) {
                            Glide.with(this@ProductDetailActivity)
                                .load(product.image)
                                .into(productImageView)
                        }

                        // Set up the Order button click listener
                        orderButton.setOnClickListener {
                            val intent = Intent(this@ProductDetailActivity, OrderActivity::class.java)
                            intent.putExtra("product_id", product.id)
                            startActivity(intent)
                        }
                    }
                } else {
                    Toast.makeText(this@ProductDetailActivity, "Failed to fetch product details", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<ProductDetailResponse>, t: Throwable) {
                Toast.makeText(this@ProductDetailActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}
