package com.example.model

enum class Biome { FOREST, DESERT, MOUNTAIN, RUINS, BEACH, DUNGEON }

enum class TileType {
    GRASS, DEEP_WATER, SHALLOW_WATER, SAND, DIRT, STONE_FLOOR, DUNGEON_WALL
}

enum class ItemType(
    val displayName: String,
    val icon: String,
    val category: String,
    val description: String
) {
    WOOD("Wood", "🪵", "Resource", "Chopped from forest trees. Used for crafting."),
    STONE("Stone", "🪨", "Resource", "Mined from mountain boulders."),
    IRON_ORE("Iron Ore", "⛓️", "Resource", "Raw iron found in caves and ruins."),
    GOLD_COINS("Gold Coins", "🪙", "Currency", "Ancient coins for traders."),
    BERRIES("Wild Berries", "🍒", "Food", "Sweet berries that restore hunger (+15) and health (+5)."),
    RAW_MEAT("Raw Meat", "🥩", "Food", "Meat from beasts. Needs cooking!"),
    COOKED_MEAT("Steak", "🍖", "Food", "Hearty meal restoring (+50) hunger and (+25) health."),
    WOOD_AXE("Wood Axe", "🪓", "Tool", "Chops trees faster and deals 15 damage."),
    IRON_SWORD("Iron Sword", "⚔️", "Weapon", "Forged blade dealing 35 critical damage."),
    BOW("Hunting Bow", "🏹", "Weapon", "Ranged weapon to strike from afar."),
    CAMPFIRE("Campfire", "🔥", "Building", "Cooks meat and provides warm night light."),
    WOOD_SHELTER("Wood Cabin", "🛖", "Building", "Safe shelter to rest and save progress."),
    CHEST("Treasure Chest", "📦", "Building", "Stores up to 20 extra items."),
    HEALTH_POTION("Health Elixir", "🧪", "Consumable", "Restores 60 Health instantly.")
}

data class CraftingRecipe(
    val result: ItemType,
    val amount: Int,
    val requirements: Map<ItemType, Int>
)

val RECIPES = listOf(
    CraftingRecipe(ItemType.WOOD_AXE, 1, mapOf(ItemType.WOOD to 5, ItemType.STONE to 3)),
    CraftingRecipe(ItemType.IRON_SWORD, 1, mapOf(ItemType.IRON_ORE to 8, ItemType.WOOD to 4)),
    CraftingRecipe(ItemType.CAMPFIRE, 1, mapOf(ItemType.WOOD to 6, ItemType.STONE to 4)),
    CraftingRecipe(ItemType.COOKED_MEAT, 1, mapOf(ItemType.RAW_MEAT to 1, ItemType.WOOD to 1)),
    CraftingRecipe(ItemType.WOOD_SHELTER, 1, mapOf(ItemType.WOOD to 25, ItemType.STONE to 10)),
    CraftingRecipe(ItemType.HEALTH_POTION, 1, mapOf(ItemType.BERRIES to 4, ItemType.IRON_ORE to 1))
)

data class WorldEntity(
    val id: Int,
    val x: Float,
    val y: Float,
    val type: String, // "TREE", "ROCK", "BERRY_BUSH", "WOLF", "GOBLIN", "CHEST", "CAMPFIRE"
    var health: Int = 100,
    val maxHealth: Int = 100
)

data class Quest(
    val title: String,
    val description: String,
    val reward: String,
    var isCompleted: Boolean = false
)
