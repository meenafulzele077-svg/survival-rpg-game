import os

# 1. Expand GameData with new Structures, Boss & Dungeon tiles
game_data_code = """package com.example.model

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
"""

with open("app/src/main/java/com/example/model/GameData.kt", "w") as f:
    f.write(game_data_code)

# 2. Update GameEngine with Building Placement, Boss Fight & Rest/Sleep
engine_code = """package com.example.engine

import androidx.compose.runtime.*
import com.example.audio.SoundFX
import com.example.model.*
import kotlin.math.*
import kotlin.random.Random

class GameEngine(var soundFx: SoundFX? = null) {
    var playerX by mutableFloatStateOf(1500f)
    var playerY by mutableFloatStateOf(1500f)
    var respawnX = 1500f
    var respawnY = 1500f
    var playerAngle by mutableFloatStateOf(0f)
    var isMoving by mutableStateOf(false)
    var isAttacking by mutableStateOf(false)
    var isGameOver by mutableStateOf(false)

    // Player Stats
    var health by mutableFloatStateOf(100f)
    var maxHealth by mutableFloatStateOf(100f)
    var hunger by mutableFloatStateOf(100f)
    var thirst by mutableFloatStateOf(100f)
    var stamina by mutableFloatStateOf(100f)
    var gold by mutableIntStateOf(30)
    var level by mutableIntStateOf(1)
    var exp by mutableIntStateOf(0)
    var dayCount by mutableIntStateOf(1)
    var timeOfDay by mutableFloatStateOf(0.15f)

    val inventory = mutableStateMapOf<ItemType, Int>().apply {
        put(ItemType.WOOD_AXE, 1)
        put(ItemType.BERRIES, 10)
        put(ItemType.WOOD, 25)
        put(ItemType.STONE, 15)
        put(ItemType.RAW_MEAT, 2)
    }
    var selectedItem by mutableStateOf<ItemType?>(ItemType.WOOD_AXE)
    var placeModeItem by mutableStateOf<ItemType?>(null)

    val entities = mutableStateListOf<WorldEntity>()
    var nextEntityId = 1000

    val quests = mutableStateListOf(
        Quest(1, "The Shipwreck Awakening", "Gather resources and craft your first Campfire.", "Exp + 50, Gold + 30"),
        Quest(2, "Homestead of Eldoria", "Build a Wood Cabin shelter to safely rest through the dark nights.", "Exp + 100, Iron Sword"),
        Quest(3, "The Ancient Ruins Boss", "Venture East to the temple ruins and vanquish the Ancient Stone Golem.", "Sun Blade (Excalibur)")
    )

    var currentDialog by mutableStateOf<String?>(
        "Old Journal: 'Beware the eastern ruins... An ancient Stone Golem awakens when intruders enter the holy circle. Build a shelter and forge an Iron Sword before exploring!'"
    )

    init {
        generateWorld()
    }

    private fun generateWorld() {
        val rng = Random(123)
        // Wilderness entities
        for (i in 0..120) {
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

        // Ancient Temple Ruins Boss Arena at East (x: 2800, y: 1500)
        entities.add(WorldEntity(9999, 2800f, 1500f, "BOSS_GOLEM", health = 450, maxHealth = 450))
        for (j in 0..4) {
            entities.add(WorldEntity(8000 + j, 2750f + rng.nextFloat() * 100f, 1450f + rng.nextFloat() * 100f, "SKELETON", 60, 60))
        }
    }

    fun tick(dt: Float) {
        if (isGameOver) return

        // Time and vitals
        timeOfDay = (timeOfDay + 0.0003f) % 1.0f
        if (timeOfDay > 0.99f) dayCount++
        hunger = (hunger - 0.006f * dt).coerceAtLeast(0f)
        thirst = (thirst - 0.008f * dt).coerceAtLeast(0f)

        // Health drain if starving
        if (hunger <= 0f || thirst <= 0f) {
            health = (health - 2f * dt).coerceAtLeast(0f)
            if (health <= 0f) isGameOver = true
        }

        // Enemy AI (Wolves, Skeletons, Boss Golem)
        for (i in entities.indices) {
            val e = entities[i]
            val dist = hypot(playerX - e.x, playerY - e.y)

            when (e.type) {
                "WOLF" -> {
                    if (dist in 40f..320f) {
                        val angle = atan2(playerY - e.y, playerX - e.x)
                        entities[i] = e.copy(x = e.x + cos(angle) * 85f * dt, y = e.y + sin(angle) * 85f * dt)
                    } else if (dist < 40f) {
                        health = (health - 12f * dt).coerceAtLeast(0f)
                        soundFx?.vibrate(25)
                        if (health <= 0f) isGameOver = true
                    }
                }
                "SKELETON" -> {
                    if (dist in 40f..350f) {
                        val angle = atan2(playerY - e.y, playerX - e.x)
                        entities[i] = e.copy(x = e.x + cos(angle) * 70f * dt, y = e.y + sin(angle) * 70f * dt)
                    } else if (dist < 40f) {
                        health = (health - 16f * dt).coerceAtLeast(0f)
                        soundFx?.vibrate(30)
                        if (health <= 0f) isGameOver = true
                    }
                }
                "BOSS_GOLEM" -> {
                    if (dist in 50f..400f) {
                        val angle = atan2(playerY - e.y, playerX - e.x)
                        entities[i] = e.copy(x = e.x + cos(angle) * 55f * dt, y = e.y + sin(angle) * 55f * dt)
                    } else if (dist < 50f) {
                        health = (health - 25f * dt).coerceAtLeast(0f)
                        soundFx?.vibrate(50)
                        if (health <= 0f) isGameOver = true
                    }
                }
            }
        }
    }

    fun updateJoystick(deltaX: Float, deltaY: Float) {
        if (deltaX == 0f && deltaY == 0f) {
            isMoving = false
            return
        }
        isMoving = true
        playerAngle = atan2(deltaY, deltaX)
        val speed = 6.8f
        playerX = (playerX + deltaX * speed).coerceIn(100f, 3900f)
        playerY = (playerY + deltaY * speed).coerceIn(100f, 3900f)
    }

    fun interactOrAttack() {
        if (isGameOver) return
        isAttacking = true

        val target = entities.minByOrNull { hypot(it.x - playerX, it.y - playerY) }
        val dist = if (target != null) hypot(target.x - playerX, target.y - playerY) else 999f

        // Interacting with placed buildings
        if (target != null && dist < 120f) {
            if (target.type == "CABIN") {
                // Sleep and skip night!
                timeOfDay = 0.15f
                dayCount++
                health = maxHealth
                hunger = (hunger + 30f).coerceAtMost(100f)
                thirst = (thirst + 30f).coerceAtMost(100f)
                respawnX = playerX
                respawnY = playerY
                currentDialog = "Rested in Cabin: Night skipped, health fully restored, and spawn point updated! ☀️"
                soundFx?.playSound("COIN")
                return
            } else if (target.type == "CAMPFIRE") {
                // Cook meat if held
                if ((inventory[ItemType.RAW_MEAT] ?: 0) > 0) {
                    val count = inventory[ItemType.RAW_MEAT] ?: 0
                    if (count <= 1) inventory.remove(ItemType.RAW_MEAT) else inventory[ItemType.RAW_MEAT] = count - 1
                    addItem(ItemType.COOKED_MEAT, 1)
                    soundFx?.playSound("CHOP")
                    currentDialog = "Campfire: Roasted raw meat into a delicious steak! 🍖"
                    return
                }
            }
        }

        // Normal Attack
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
            soundFx?.vibrate(40)

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
                        currentDialog = "VICTORY! The Ancient Golem has crumbled! You obtained the legendary SUN BLADE (Excalibur)! 🗡️"
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

        // Place right in front of player
        val px = playerX + cos(playerAngle) * 80f
        val py = playerY + sin(playerAngle) * 80f

        entities.add(WorldEntity(nextEntityId++, px, py, buildingType, 100, 100))
        if (count <= 1) inventory.remove(item) else inventory[item] = count - 1
        soundFx?.playSound("CHOP")
        soundFx?.vibrate(50)

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
            currentDialog = "LEVEL UP! You reached Level $level! Max HP increased! ⭐"
        }
    }

    fun respawn() {
        health = maxHealth
        hunger = 80f
        thirst = 80f
        playerX = respawnX
        playerY = respawnY
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
        soundFx?.vibrate(45)
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
"""

with open("app/src/main/java/com/example/engine/GameEngine.kt", "w") as f:
    f.write(engine_code)

# 3. Update GameCanvas to draw Skeletons, Boss Golem, Campfires, and Cabins
with open("app/src/main/java/com/example/ui/GameCanvas.kt", "r") as f:
    canvas_code = f.read()

# Add Boss and Placed Building drawings
canvas_enhancement = """
                "CAMPFIRE" -> {
                    // Burning Campfire
                    drawCircle(Color(0xFF424242), 22f, Offset(drawX, drawY + 4f))
                    drawCircle(Color(0xFFFF9800), 16f, Offset(drawX, drawY - 2f))
                    drawCircle(Color(0xFFFFEB3B), 9f, Offset(drawX, drawY - 4f))
                }
                "CABIN" -> {
                    // Wood Cabin Shelter
                    drawRoundRect(Color(0xFF5D4037), Offset(drawX - 35f, drawY - 25f), Size(70f, 50f), CornerRadius(8f, 8f))
                    drawRoundRect(Color(0xFF795548), Offset(drawX - 30f, drawY - 45f), Size(60f, 25f), CornerRadius(6f, 6f)) // Roof
                    drawRect(Color(0xFF2E1B0E), Offset(drawX - 10f, drawY), Size(20f, 25f)) // Door
                }
                "SKELETON" -> {
                    // Skeleton Dungeon Guardian
                    drawCircle(Color(0xFFE0E0E0), 10f, Offset(drawX, drawY - 18f))
                    drawRoundRect(Color(0xFFBDBDBD), Offset(drawX - 10f, drawY - 8f), Size(20f, 24f), CornerRadius(4f, 4f))
                    val fill = (e.health.toFloat() / e.maxHealth.toFloat()).coerceIn(0f, 1f)
                    drawRect(Color.Red, Offset(drawX - 15f, drawY - 32f), Size(30f * fill, 3f))
                }
                "BOSS_GOLEM" -> {
                    // Huge Ancient Stone Golem Boss
                    drawOval(Color(0x77000000), Offset(drawX - 45f, drawY + 28f), Size(90f, 30f))
                    drawRoundRect(Color(0xFF455A64), Offset(drawX - 35f, drawY - 35f), Size(70f, 65f), CornerRadius(16f, 16f))
                    drawCircle(Color(0xFF00E5FF), 5f, Offset(drawX - 12f, drawY - 15f)) // Glowing Cyan Eye
                    drawCircle(Color(0xFF00E5FF), 5f, Offset(drawX + 12f, drawY - 15f))
                    // Big Boss Health Bar
                    drawRoundRect(Color(0xCC000000), Offset(drawX - 50f, drawY - 55f), Size(100f, 10f), CornerRadius(4f, 4f))
                    val fill = (e.health.toFloat() / e.maxHealth.toFloat()).coerceIn(0f, 1f)
                    drawRoundRect(Color(0xFFFF1744), Offset(drawX - 50f, drawY - 55f), Size(100f * fill, 10f), CornerRadius(4f, 4f))
                }
"""

canvas_code = canvas_code.replace('"CHEST" -> {', canvas_enhancement + '\n                "CHEST" -> {')

with open("app/src/main/java/com/example/ui/GameCanvas.kt", "w") as f:
    f.write(canvas_code)

# 4. Add Game Over Respawn Screen & Building Placement to MainGameScreen.kt
with open("app/src/main/java/com/example/ui/MainGameScreen.kt", "r") as f:
    screen_code = f.read()

# Add Game Over Overlay
game_over_ui = """
        // Game Over Respawn Modal
        if (engine.isGameOver) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color(0xDD000000)),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("💀 YOU PERISHED", color = Color(0xFFFF1744), fontSize = 28.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("The wilderness of Eldoria overcame you...", color = Color.LightGray, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(20.dp))
                    Button(
                        onClick = { engine.respawn() },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
                    ) {
                        Text("Respawn at Camp ⛺", fontSize = 16.sp)
                    }
                }
            }
        }
"""

screen_code = screen_code.replace(
    "if (showCrafting) {",
    game_over_ui + "\n        if (showCrafting) {"
)

# Update hotbar click so building items place directly into the world
screen_code = screen_code.replace(
    'if (item.category == "Food" || item.category == "Consumable") {\\n                                engine.consumeItem(item)\\n                            }',
    'if (item.category == "Food" || item.category == "Consumable") {\\n                                engine.consumeItem(item)\\n                            } else if (item.category == "Building") {\\n                                engine.placeBuilding(item)\\n                            }'
)

with open("app/src/main/java/com/example/ui/MainGameScreen.kt", "w") as f:
    f.write(screen_code)

print("✨ PART 3 ADVENTURE & BOSS OVERHAUL READY!")
