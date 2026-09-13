package com.example.model

enum class ItemType(
    val displayName: String,
    val icon: String,
    val category: String,
    val description: String
) {
    WOOD("Wood", "🪵", "Resource", "Chopped from forest trees. Used for building and fires."),
    STONE("Stone", "🪨", "Resource", "Mined from boulders. Used for sturdy construction."),
    IRON_ORE("Iron Ore", "⛓️", "Resource", "Mined from glowing mineral veins."),
    GOLD_COINS("Gold Coins", "🪙", "Currency", "Valuable treasure recovered from ruins."),
    BERRIES("Wild Berries", "🍒", "Food", "Restores hunger (+15) and health (+5)."),
    RAW_MEAT("Raw Meat", "🥩", "Food", "Beast meat. Must cook on a campfire!"),
    COOKED_MEAT("Roasted Steak", "🍖", "Food", "Delicious meal restoring (+50) hunger & (+30) health."),
    WOOD_AXE("Wood Axe", "🪓", "Tool", "Essential for harvesting timber."),
    IRON_SWORD("Iron Sword", "⚔️", "Weapon", "High-damage blade against dungeon monsters."),
    EXCALIBUR("Sun Blade", "🗡️", "Legendary", "Ancient holy sword dealing 85 critical damage!"),
    CAMPFIRE("Campfire", "🔥", "Building", "Place to illuminate night and cook meat."),
    WOOD_CABIN("Wood Cabin", "🛖", "Building", "Place to sleep, skip night, and heal."),
    CHEST("Storage Chest", "📦", "Building", "Place in your camp to store items."),
    HEALTH_POTION("Health Elixir", "🧪", "Consumable", "Restores 60 Health instantly.")
}

data class CraftingRecipe(
    val result: ItemType,
    val amount: Int,
    val requirements: Map<ItemType, Int>
)

val RECIPES = listOf(
    CraftingRecipe(ItemType.WOOD_AXE, 1, mapOf(ItemType.WOOD to 5, ItemType.STONE to 3)),
    CraftingRecipe(ItemType.IRON_SWORD, 1, mapOf(ItemType.IRON_ORE to 6, ItemType.WOOD to 4)),
    CraftingRecipe(ItemType.CAMPFIRE, 1, mapOf(ItemType.WOOD to 6, ItemType.STONE to 4)),
    CraftingRecipe(ItemType.COOKED_MEAT, 1, mapOf(ItemType.RAW_MEAT to 1, ItemType.WOOD to 1)),
    CraftingRecipe(ItemType.WOOD_CABIN, 1, mapOf(ItemType.WOOD to 20, ItemType.STONE to 10)),
    CraftingRecipe(ItemType.CHEST, 1, mapOf(ItemType.WOOD to 12, ItemType.STONE to 4)),
    CraftingRecipe(ItemType.HEALTH_POTION, 1, mapOf(ItemType.BERRIES to 4, ItemType.IRON_ORE to 1))
)

data class WorldEntity(
    val id: Int,
    var x: Float,
    var y: Float,
    val type: String, // "TREE", "ROCK", "BERRY_BUSH", "WOLF", "SKELETON", "BOSS_GOLEM", "CAMPFIRE", "CABIN", "CHEST"
    var health: Int = 100,
    val maxHealth: Int = 100
)

data class Quest(
    val id: Int,
    val title: String,
    val description: String,
    val reward: String,
    var isCompleted: Boolean = false
)
