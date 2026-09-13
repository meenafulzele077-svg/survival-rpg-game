package com.example.engine

import androidx.compose.runtime.*
import com.example.audio.SoundFX
import com.example.model.*
import kotlin.math.*
import kotlin.random.Random

class GameEngine(var soundFx: SoundFX? = null) {
    // Game World State (Direct fast floats for 60fps rendering without Compose lag)
    var rawPlayerX = 1500f
    var rawPlayerY = 1500f
    var rawAngle = 0f
    var rawIsMoving = false
    var rawIsAttacking = false

    var respawnX = 1500f
    var respawnY = 1500f
    var isGameOver by mutableStateOf(false)

    // UI Observable States (Only recompose UI when stats actually change!)
    var health by mutableFloatStateOf(100f)
    var maxHealth by mutableFloatStateOf(100f)
    var hunger by mutableFloatStateOf(100f)
    var thirst by mutableFloatStateOf(100f)
    var gold by mutableIntStateOf(30)
    var level by mutableIntStateOf(1)
    var exp by mutableIntStateOf(0)
    var dayCount by mutableIntStateOf(1)
    var timeOfDay = 0.15f

    val inventory = mutableStateMapOf<ItemType, Int>().apply {
        put(ItemType.WOOD_AXE, 1)
        put(ItemType.BERRIES, 10)
        put(ItemType.WOOD, 25)
        put(ItemType.STONE, 15)
        put(ItemType.RAW_MEAT, 2)
    }
    var selectedItem by mutableStateOf<ItemType?>(ItemType.WOOD_AXE)

    val entities = mutableStateListOf<WorldEntity>()
    var nextEntityId = 1000

    val quests = mutableStateListOf(
        Quest(1, "The Awakening", "Craft your first Campfire using Wood & Stone.", "Exp + 50, Gold + 30"),
        Quest(2, "Homestead", "Build a Wood Cabin shelter to sleep through nights.", "Exp + 100, Iron Sword"),
        Quest(3, "Ancient Ruins", "Venture East and defeat the Ancient Stone Golem Boss.", "Sun Blade (Excalibur)")
    )

    var currentDialog by mutableStateOf<String?>(
        "Old Journal: 'Beware the eastern ruins... An ancient Stone Golem awakens when intruders enter. Build a shelter and forge an Iron Sword first!'"
    )

    init {
        generateWorld()
    }

    private fun generateWorld() {
        val rng = Random(123)
        for (i in 0..110) {
            val ex = rng.nextFloat() * 3200f + 200f
            val ey = rng.nextFloat() * 3200f + 200f
            val type = when (rng.nextInt(6)) {
                0, 1 -> "TREE"
                2 -> "ROCK"
                3 -> "BERRY_BUSH"
                4 -> "WOLF"
                else -> "CHEST"
            }
            entities.add(WorldEntity(i, ex, ey, type, if (type == "WOLF") 80 else 50))
        }

        // Boss Arena
        entities.add(WorldEntity(9999, 2800f, 1500f, "BOSS_GOLEM", 450, 450))
        for (j in 0..3) {
            entities.add(WorldEntity(8000 + j, 2750f + rng.nextFloat() * 100f, 1450f + rng.nextFloat() * 100f, "SKELETON", 60, 60))
        }
    }

    fun updateJoystick(deltaX: Float, deltaY: Float) {
        if (deltaX == 0f && deltaY == 0f) {
            rawIsMoving = false
            return
        }
        rawIsMoving = true
        rawAngle = atan2(deltaY, deltaX)
        val speed = 7.5f
        rawPlayerX = (rawPlayerX + deltaX * speed).coerceIn(100f, 3900f)
        rawPlayerY = (rawPlayerY + deltaY * speed).coerceIn(100f, 3900f)
    }

    fun tick(dt: Float) {
        if (isGameOver) return

        timeOfDay = (timeOfDay + 0.0003f) % 1.0f

        // Vitals drain slowly
        hunger = (hunger - 0.004f * dt).coerceAtLeast(0f)
        thirst = (thirst - 0.006f * dt).coerceAtLeast(0f)
        if (hunger <= 0f || thirst <= 0f) {
            health = (health - 2f * dt).coerceAtLeast(0f)
            if (health <= 0f) isGameOver = true
        }

        // Fast Enemy AI
        for (i in entities.indices) {
            val e = entities[i]
            val dist = hypot(rawPlayerX - e.x, rawPlayerY - e.y)

            when (e.type) {
                "WOLF" -> {
                    if (dist in 40f..300f) {
                        val angle = atan2(rawPlayerY - e.y, rawPlayerX - e.x)
                        entities[i] = e.copy(x = e.x + cos(angle) * 80f * dt, y = e.y + sin(angle) * 80f * dt)
                    } else if (dist < 40f) {
                        health = (health - 10f * dt).coerceAtLeast(0f)
                        if (health <= 0f) isGameOver = true
                    }
                }
                "SKELETON" -> {
                    if (dist in 40f..320f) {
                        val angle = atan2(rawPlayerY - e.y, rawPlayerX - e.x)
                        entities[i] = e.copy(x = e.x + cos(angle) * 70f * dt, y = e.y + sin(angle) * 70f * dt)
                    } else if (dist < 40f) {
                        health = (health - 14f * dt).coerceAtLeast(0f)
                        if (health <= 0f) isGameOver = true
                    }
                }
                "BOSS_GOLEM" -> {
                    if (dist in 50f..380f) {
                        val angle = atan2(rawPlayerY - e.y, rawPlayerX - e.x)
                        entities[i] = e.copy(x = e.x + cos(angle) * 50f * dt, y = e.y + sin(angle) * 50f * dt)
                    } else if (dist < 50f) {
                        health = (health - 22f * dt).coerceAtLeast(0f)
                        if (health <= 0f) isGameOver = true
                    }
                }
            }
        }
    }

    fun interactOrAttack() {
        if (isGameOver) return
        rawIsAttacking = true

        val target = entities.minByOrNull { hypot(it.x - rawPlayerX, it.y - rawPlayerY) }
        val dist = if (target != null) hypot(target.x - rawPlayerX, target.y - rawPlayerY) else 999f

        // Placed Buildings
        if (target != null && dist < 120f) {
            if (target.type == "CABIN") {
                timeOfDay = 0.15f
                dayCount++
                health = maxHealth
                hunger = 100f
                thirst = 100f
                respawnX = rawPlayerX
                respawnY = rawPlayerY
                currentDialog = "Rested in Cabin: Night skipped, health fully restored! ☀️"
                soundFx?.playSound("COIN")
                return
            } else if (target.type == "CAMPFIRE") {
                if ((inventory[ItemType.RAW_MEAT] ?: 0) > 0) {
                    val count = inventory[ItemType.RAW_MEAT] ?: 0
                    if (count <= 1) inventory.remove(ItemType.RAW_MEAT) else inventory[ItemType.RAW_MEAT] = count - 1
                    addItem(ItemType.COOKED_MEAT, 1)
                    soundFx?.playSound("CHOP")
                    currentDialog = "Campfire: Roasted raw meat into a savory steak! 🍖"
                    return
                }
            }
        }

        soundFx?.playSound("SLASH")
        if (target != null && dist < 140f) {
            val dmg = when (selectedItem) {
                ItemType.EXCALIBUR -> 85
                ItemType.IRON_SWORD -> 40
                ItemType.WOOD_AXE -> 22
                else -> 12
            }
            target.health -= dmg
            soundFx?.playSound(if (target.type == "ROCK" || target.type == "BOSS_GOLEM") "MINE" else "HIT")
            soundFx?.vibrate(35)

            if (target.health <= 0) {
                when (target.type) {
                    "TREE" -> addItem(ItemType.WOOD, 5)
                    "ROCK" -> { addItem(ItemType.STONE, 3); if (Random.nextBoolean()) addItem(ItemType.IRON_ORE, 2) }
                    "BERRY_BUSH" -> addItem(ItemType.BERRIES, 4)
                    "WOLF" -> { addItem(ItemType.RAW_MEAT, 2); addExp(30) }
                    "SKELETON" -> { addItem(ItemType.GOLD_COINS, 15); addExp(40) }
                    "BOSS_GOLEM" -> {
                        addItem(ItemType.EXCALIBUR, 1)
                        addItem(ItemType.GOLD_COINS, 100)
                        addExp(200)
                        quests[2].isCompleted = true
                        currentDialog = "VICTORY! The Ancient Golem has fallen! You obtained the SUN BLADE! 🗡️"
                    }
                    "CHEST" -> { addItem(ItemType.GOLD_COINS, 30); addItem(ItemType.HEALTH_POTION, 2); soundFx?.playSound("COIN") }
                }
                entities.remove(target)
            }
        }
    }

    fun placeBuilding(item: ItemType) {
        val count = inventory[item] ?: 0
        if (count <= 0) return

        val buildingType = when (item) {
            ItemType.CAMPFIRE -> "CAMPFIRE"
            ItemType.WOOD_CABIN -> "CABIN"
            ItemType.CHEST -> "CHEST"
            else -> return
        }

        val px = rawPlayerX + cos(rawAngle) * 80f
        val py = rawPlayerY + sin(rawAngle) * 80f

        entities.add(WorldEntity(nextEntityId++, px, py, buildingType, 100, 100))
        if (count <= 1) inventory.remove(item) else inventory[item] = count - 1
        soundFx?.playSound("CHOP")

        if (item == ItemType.CAMPFIRE) quests[0].isCompleted = true
        if (item == ItemType.WOOD_CABIN) quests[1].isCompleted = true
    }

    fun addExp(amount: Int) {
        exp += amount
        if (exp >= 100) {
            level++
            exp = 0
            maxHealth += 25
            health = maxHealth
            soundFx?.playSound("COIN")
            currentDialog = "LEVEL UP! Reached Level $level! Max HP boosted! ⭐"
        }
    }

    fun respawn() {
        health = maxHealth
        hunger = 100f
        thirst = 100f
        rawPlayerX = respawnX
        rawPlayerY = respawnY
        isGameOver = false
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
        soundFx?.playSound("MINE")
        addExp(20)
        return true
    }

    fun consumeItem(item: ItemType) {
        val count = inventory[item] ?: return
        when (item) {
            ItemType.BERRIES -> { hunger = (hunger + 15f).coerceAtMost(100f); health = (health + 5f).coerceAtMost(maxHealth) }
            ItemType.COOKED_MEAT -> { hunger = (hunger + 50f).coerceAtMost(100f); health = (health + 30f).coerceAtMost(maxHealth) }
            ItemType.HEALTH_POTION -> { health = (health + 60f).coerceAtMost(maxHealth) }
            else -> return
        }
        if (count <= 1) inventory.remove(item) else inventory[item] = count - 1
    }

    fun addItem(item: ItemType, qty: Int) {
        inventory[item] = (inventory[item] ?: 0) + qty
    }
}
