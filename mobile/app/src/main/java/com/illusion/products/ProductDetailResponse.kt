package com.illusion.products

data class ProductDetailResponse(
    val id: Int,
    val description: String,
    val price: Double,
    val image: String? // Base64-encoded string for image
)
