package com.illusion.orders

data class OrderSummaryResponse(
    val totalOrders: Int,
    val totalSum: Double,
    val ordersPerProvince: Map<String, Int>
)
