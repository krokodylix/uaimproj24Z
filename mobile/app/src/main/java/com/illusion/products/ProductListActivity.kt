package com.illusion.products

import android.app.AlertDialog
import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.example.agromobile.R
import com.illusion.auth.LoginActivity
import com.illusion.admin.ReportActivity
import com.illusion.network.ApiService
import com.illusion.network.UserResponse
import com.illusion.utils.SessionManager
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ProductListActivity : AppCompatActivity() {
    private lateinit var sessionManager: SessionManager
    private var isAdmin: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product_list)

        sessionManager = SessionManager(this)

        val usernameTextView = findViewById<TextView>(R.id.usernameTextView)
        val productListView = findViewById<ListView>(R.id.productListView)
        val logoutButton = findViewById<Button>(R.id.logoutButton)
        val addProductButton = findViewById<Button>(R.id.addProductButton)
        val generateReportButton = findViewById<Button>(R.id.generateReportButton)

        // Fetch user details to check if admin
        val token = sessionManager.getToken()
        if (token != null) {
            ApiService.instance.getUserDetails("Bearer $token").enqueue(object : Callback<UserResponse> {
                override fun onResponse(call: Call<UserResponse>, response: Response<UserResponse>) {
                    if (response.isSuccessful) {
                        val user = response.body()
                        if (user != null) {
                            isAdmin = user.is_admin
                            usernameTextView.text = "Welcome, ${user.username}!"

                            // Show admin-specific buttons
                            addProductButton.visibility = if (isAdmin) Button.VISIBLE else Button.GONE
                            generateReportButton.visibility = if (isAdmin) Button.VISIBLE else Button.GONE
                        }
                    } else {
                        Toast.makeText(this@ProductListActivity, "Failed to fetch user details", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<UserResponse>, t: Throwable) {
                    Toast.makeText(this@ProductListActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }

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

        // Handle add product
        addProductButton.setOnClickListener {
            if (isAdmin) {
                showAddProductDialog()
            }
        }

        // Handle logout
        logoutButton.setOnClickListener {
            sessionManager.clearSession()
            val intent = Intent(this, LoginActivity::class.java)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            startActivity(intent)
        }

        // Handle generate report
        generateReportButton.setOnClickListener {
            if (isAdmin) {
                val intent = Intent(this, ReportActivity::class.java)
                startActivity(intent)
            }
        }
    }

    private fun showAddProductDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_add_product, null)
        val descriptionInput = dialogView.findViewById<EditText>(R.id.productDescriptionInput)
        val priceInput = dialogView.findViewById<EditText>(R.id.productPriceInput)

        AlertDialog.Builder(this)
            .setTitle("Add New Product")
            .setView(dialogView)
            .setPositiveButton("Add") { _, _ ->
                val description = descriptionInput.text.toString()
                val price = priceInput.text.toString().toDoubleOrNull()

                if (description.isBlank() || price == null) {
                    Toast.makeText(this, "Invalid input", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }

                // Call API to add product
                val token = sessionManager.getToken()
                if (token != null) {
                    ApiService.instance.addProduct("Bearer $token", Product(description = description, price = price, image = null))
                        .enqueue(object : Callback<Void> {
                            override fun onResponse(call: Call<Void>, response: Response<Void>) {
                                if (response.isSuccessful) {
                                    Toast.makeText(this@ProductListActivity, "Product added successfully", Toast.LENGTH_SHORT).show()
                                    recreate() // Refresh the activity
                                } else {
                                    Toast.makeText(this@ProductListActivity, "Failed to add product", Toast.LENGTH_SHORT).show()
                                }
                            }

                            override fun onFailure(call: Call<Void>, t: Throwable) {
                                Toast.makeText(this@ProductListActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                            }
                        })
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
