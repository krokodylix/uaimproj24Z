package com.illusion.products

import android.content.Intent
import android.os.Bundle
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.ListView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.agromobile.R
import com.illusion.network.ApiService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ProductListActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_list)

        val productListView = findViewById<ListView>(R.id.productListView)

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
    }
}
