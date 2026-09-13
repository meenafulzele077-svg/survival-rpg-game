package com.example.engine

import androidx.compose.runtime.*
import com.example.model.*
import kotlin.math.*
import kotlin.random.Random

class GameEngine {
    // Player coordinates in huge open world (5000 x 5000 units)
    var playerX by mutableFloatStateOf(1200f)
    var playerY by mutableFloatStateOf(1200f)
    var playerAngle by mutableFloatStateOf(0f)
    var isMoving by mutableStateOf(false)
    var isAttacking by mutableStateOf(false)

    // Player Survival Stats
    var health by mutableFloatStateOf(100f)
    var maxHealth by mutableFloatStateOf(100f)
    var hunger by mutableFloatStateOf(100f)
    var thirst by mutableFloatStateOf(100f)
    var stamina by mutableFloatStateOf(100f)
    var gold by mutableIntStateOf(15)
    var level by mutableIntStateOf(1)
    var exp by mutableIntStateOf(0)
    var dayCount by mutableIntStateOf(1)
    var timeOfDay by mutableFloatStateOf(0.2f) // 0.0 to 1.0 (Day -> Dusk -> Night)

    // Inventory: item to count
    val inventory = mutableStateMapOf<ItemType, Int>().apply {
        put(ItemType.WOOD_AXE, 1)
        put(ItemType.BERRIES, 6)
        put(ItemType.WOOD, 10)
    }
    var selectedItem by mutableStateOf<ItemType?>(ItemType.WOOD_AXE)

    // World Entities (Trees, Rocks, Mobs, Chests)
    val entities = mutableStateListOf<WorldEntity>()
    val floatingTexts = mutableStateListOf<Pair<String, Pair<Float, Float>>>()

    // Story Quests
    val quests = mutableStateListOf(
        Quest("The Shipwreck Awakening", "Gather 10 Wood and 6 Stone to build your first campfire.", "Gold + 25, Exp + 50"),
        Quest("Beast of the Twilight", "Slay 3 shadow wolves roaming the ruined shrine.", "Iron Sword + 1"),
        Quest("The Ancient Dungeon Key", "Discover the hidden temple ruins deep in the eastern mountains.", "Eldoria Relic")
    )

    var currentDialog by mutableStateOf<String?>(
        "Old Journal: 'I awakened on the cursed shores of Eldoria... Shadows hunt after dusk. I must harvest wood, craft weapons, and uncover the sunken temple...'"
    )

    init {
        generateWorld()
    }

    private fun generateWorld() {
        val rng = Random(42)
        // Spawn 60 trees, rocks, beasts across the map
        for (i in 0..120) {
            val ex = rng.nextFloat() * 3000f + 200f
            val ey = rng.nextFloat() * 3000f + 200f
            val type = when (rng.nextInt(5)) {
                0, 1 -> "TREE"
                2 -> "ROCK"
                3 -> "BERRY_BUSH"
                else -> if (rng.nextBoolean()) "WOLF" else "CHEST"
            }
            entities.add(WorldEntity(i, ex, ey, type, if (type == "WOLF") 80 else 50))
        }
    }

    fun updateJoystick(deltaX: Float, deltaY: Float) {
        if (deltaX == 0f && deltaY == 0f) {
            isMoving = false
            return
        }
        isMoving = true
        playerAngle = atan2(deltaY, deltaX)
        val speed = if (stamina > 10f) 6.5f else 3.8f
        playerX = (playerX + deltaX * speed).coerceIn(100f, 3900f)
        playerY = (playerY + deltaY * speed).coerceIn(100f, 3900f)

        // Passive hunger and thirst burn
        hunger = (hunger - 0.005f).coerceAtLeast(0f)
        thirst = (thirst - 0.007f).coerceAtLeast(0f)
        timeOfDay = (timeOfDay + 0.0003f) % 1.0f
        if (timeOfDay > 0.99f) dayCount++
    }

    fun interactOrAttack() {
        isAttacking = true
        // Find entity closest to player within reach
        val target = entities.minByOrNull {
            hypot(it.x - playerX, it.y - playerY)
        }

        if (target != null && hypot(target.x - playerX, target.y - playerY) < 140f) {
            val dmg = if (selectedItem == ItemType.IRON_SWORD) 35 else if (selectedItem == ItemType.WOOD_AXE) 20 else 10
            target.health -= dmg

            if (target.health <= 0) {
                // Drop loot
                when (target.type) {
                    "TREE" -> addItem(ItemType.WOOD, 4)
                    "ROCK" -> addItem(ItemType.STONE, 3)
                    "BERRY_BUSH" -> addItem(ItemType.BERRIES, 3)
                    "WOLF" -> {
                        addItem(ItemType.RAW_MEAT, 2)
                        exp += 25
                        if (exp >= 100) { level++; exp = 0; maxHealth += 20; health = maxHealth }
                    }
                    "CHEST" -> {
                        addItem(ItemType.GOLD_COINS, 20)
                        addItem(ItemType.HEALTH_POTION, 1)
                    }
                }
                entities.remove(target)
            }
        }
    }

    fun craft(recipe: CraftingRecipe): Boolean {
        for ((item, count) in recipe.requirements) {
            if ((inventory[item] ?: 0) < count) return false
        }
        for ((item, count) in recipe.requirements) {
            val cur = inventory[item] ?: 0
            if (cur <= count) inventory.remove(item) else inventory[item] = cur - count
        }
        addItem(recipe.result, recipe.amount)
        exp += 15
        return true
    }

    fun consumeItem(item: ItemType) {
        val count = inventory[item] ?: return
        when (item) {
            ItemType.BERRIES -> {
                hunger = (hunger + 15f).coerceAtMost(100f)
                health = (health + 5f).coerceAtMost(maxHealth)
            }
            ItemType.COOKED_MEAT -> {
                hunger = (hunger + 50f).coerceAtMost(100f)
                health = (health + 25f).coerceAtMost(maxHealth)
            }
            ItemType.HEALTH_POTION -> {
                health = (health + 60f).coerceAtMost(maxHealth)
            }
            else -> return
        }
        if (count <= 1) inventory.remove(item) else inventory[item] = count - 1
    }

    fun addItem(item: ItemType, qty: Int) {
        inventory[item] = (inventory[item] ?: 0) + qty
    }
}
