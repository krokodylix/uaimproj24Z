package com.illusion.network

import com.illusion.orders.Order
import com.illusion.orders.OrderSummaryResponse
import com.illusion.products.Product
import com.illusion.products.ProductDetailResponse
import com.illusion.products.ProductResponse
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiServiceInterface {
    @POST("/login")
    fun login(@Body loginRequest: LoginRequest): Call<LoginResponse>

    @POST("/register")
    fun register(@Body registrationRequest: RegistrationRequest): Call<Void>

    @POST("/order")
    fun createOrder(@Body order: Map<String, Any>): Call<Void>

    @GET("/orders")
    fun getOrders(): Call<List<Order>>

    @GET("/admin/report")
    fun getOrderSummary(
        @Query("start_date") startDate: String,
        @Query("end_date") endDate: String
    ): Call<OrderSummaryResponse>

    @GET("/product/{product_id}")
    fun getProductDetails(@Path("product_id") productId: Int): Call<ProductDetailResponse>

    @GET("/products")
    fun getAllProducts(): Call<List<ProductResponse>>

    @GET("/user")
    fun getUserDetails(@Header("Authorization") token: String): Call<UserResponse>


}