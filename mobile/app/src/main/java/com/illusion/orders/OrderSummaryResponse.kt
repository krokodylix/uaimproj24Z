package com.illusion.orders

data class OrderSummaryResponse(
    val order_id: Int,
    val total_sum: Double,
    val province: String
)
