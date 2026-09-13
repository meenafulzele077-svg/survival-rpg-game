package com.example.model

data class PlayerEquipment(
    var helmet: String = "Leather Cap",
    var armor: String = "Chainmail",
    var weapon: String = "Wood Axe",
    var shield: String = "Wooden Buckler"
) {
    val totalDefense: Int
        get() = (if (armor == "Chainmail") 15 else 5) + (if (shield == "Iron Shield") 12 else 4)
    val totalBonusAttack: Int
        get() = if (weapon == "Sun Blade") 60 else if (weapon == "Iron Sword") 25 else 8
}
