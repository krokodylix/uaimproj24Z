package com.illusion.orders

data class OrderSummaryResponse(
    val order_id: Int,
    val total_sum: Double,
    val province: String,
    val productImageUrl: String,
    val product_description: String,
    val address: String,
    val transport_type: String,
    val delivery_date: String,
    val product_id: Int,
    val image: String? = null // Optional field for image
)