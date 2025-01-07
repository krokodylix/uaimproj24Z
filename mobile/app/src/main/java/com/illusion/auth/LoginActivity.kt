package com.illusion.auth

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.agromobile.R
import com.illusion.products.ProductListActivity
import com.illusion.utils.SessionManager
import com.illusion.network.ApiService
import com.illusion.network.LoginRequest
import com.illusion.network.LoginResponse
import com.illusion.network.UserResponse
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class LoginActivity : AppCompatActivity() {
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        sessionManager = SessionManager(this)

        // If a valid session exists, navigate to the ProductListActivity
        if (sessionManager.isLoggedIn() && !sessionManager.getUsername().isNullOrBlank()) {
            navigateToProductList()
            return
        }

        val emailInput = findViewById<EditText>(R.id.emailInput)
        val passwordInput = findViewById<EditText>(R.id.passwordInput)
        val loginButton = findViewById<Button>(R.id.loginButton)
        val registerButton = findViewById<Button>(R.id.registerButton)

        loginButton.setOnClickListener {
            val email = emailInput.text.toString()
            val password = passwordInput.text.toString()

            if (email.isBlank() || password.isBlank()) {
                Toast.makeText(this, "Email and password are required", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            val loginRequest = LoginRequest(email, password)

            // Retrofit call to login
            ApiService.instance.login(loginRequest).enqueue(object : Callback<LoginResponse> {
                override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>) {
                    if (response.isSuccessful) {
                        val accessToken = response.body()?.access_token ?: ""
                        sessionManager.saveToken(accessToken)

                        // Fetch user details
                        ApiService.instance.getUserDetails("Bearer $accessToken").enqueue(object : Callback<UserResponse> {
                            override fun onResponse(call: Call<UserResponse>, userResponse: Response<UserResponse>) {
                                Log.d("TAG", accessToken)
                                if (userResponse.isSuccessful) {
                                    val username = userResponse.body()?.username ?: "Unknown User"
                                    sessionManager.saveUserSession(username)
                                    navigateToProductList()
                                } else {
                                    Toast.makeText(this@LoginActivity, "Failed to fetch user details", Toast.LENGTH_SHORT).show()
                                }
                            }

                            override fun onFailure(call: Call<UserResponse>, t: Throwable) {
                                Toast.makeText(this@LoginActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                            }
                        })
                    } else {
                        Toast.makeText(this@LoginActivity, "Login failed", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                    Toast.makeText(this@LoginActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }

        registerButton.setOnClickListener {
            val intent = Intent(this, RegistrationActivity::class.java)
            startActivity(intent)
        }
    }

    private fun navigateToProductList() {
        val intent = Intent(this, ProductListActivity::class.java)
        startActivity(intent)
        finish()
    }
}
