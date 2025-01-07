package com.illusion.products

import android.content.Intent
import android.os.Bundle
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.ListView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.agromobile.R
import com.illusion.auth.LoginActivity
import com.illusion.network.ApiService
import com.illusion.utils.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ProductListActivity : AppCompatActivity() {
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_list)

        sessionManager = SessionManager(this)

        val usernameTextView = findViewById<TextView>(R.id.usernameTextView)
        val productListView = findViewById<ListView>(R.id.productListView)
        val logoutButton = findViewById<Button>(R.id.logoutButton)

        // Display username
        val username = sessionManager.getUsername() ?: "Guest"
        usernameTextView.text = "Welcome, $username!"

        // Fetch products from backend
        ApiService.instance.getAllProducts().enqueue(object : Callback<List<ProductResponse>> {
            override fun onResponse(call: Call<List<ProductResponse>>, response: Response<List<ProductResponse>>) {
                if (response.isSuccessful) {
                    val products = response.body() ?: emptyList()

                    // Populate ListView
                    val productDescriptions = products.map { "${it.description} - ${it.price} PLN" }
                    val adapter = ArrayAdapter(this@ProductListActivity, android.R.layout.simple_list_item_1, productDescriptions)
                    productListView.adapter = adapter

                    // Handle product selection
                    productListView.onItemClickListener = AdapterView.OnItemClickListener { _, _, position, _ ->
                        val selectedProduct = products[position]
                        val intent = Intent(this@ProductListActivity, ProductDetailActivity::class.java)
                        intent.putExtra("product_id", selectedProduct.id)
                        startActivity(intent)
                    }
                } else {
                    Toast.makeText(this@ProductListActivity, "Failed to fetch products", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<ProductResponse>>, t: Throwable) {
                Toast.makeText(this@ProductListActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })

        // Handle logout
        logoutButton.setOnClickListener {
            sessionManager.clearSession()
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
        }
    }
}
