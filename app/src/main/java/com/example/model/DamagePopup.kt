package com.example.model

data class DamagePopup(
    val id: Long,
    val text: String,
    val x: Float,
    var y: Float,
    val colorHex: Long,
    var alpha: Float = 1.0f
)
