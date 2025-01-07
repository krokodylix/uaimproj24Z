package com.illusion.orders

data class Order(
    val id: Int,
    val productId: Int,
    val deliveryDate: String,
    val address: String,
    val transportType: String
)