package com.illusion.products

data class Product(
    val id: Int? = null, // Make id nullable with a default value of null
    val description: String,
    val price: Double,
    val image: String? = null // Optional field for image
)
