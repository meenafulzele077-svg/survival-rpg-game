# 1. Update GameEngine to handle Floating Popups & Sound Trigger
engine_code = """package com.example.engine

import androidx.compose.runtime.*
import com.example.audio.SoundFX
import com.example.model.*
import kotlin.math.*
import kotlin.random.Random

class GameEngine(var soundFx: SoundFX? = null) {
    var playerX by mutableFloatStateOf(1200f)
    var playerY by mutableFloatStateOf(1200f)
    var playerAngle by mutableFloatStateOf(0f)
    var isMoving by mutableStateOf(false)
    var isAttacking by mutableStateOf(false)

    // Survival Stats
    var health by mutableFloatStateOf(100f)
    var maxHealth by mutableFloatStateOf(100f)
    var hunger by mutableFloatStateOf(100f)
    var thirst by mutableFloatStateOf(100f)
    var stamina by mutableFloatStateOf(100f)
    var gold by mutableIntStateOf(25)
    var level by mutableIntStateOf(1)
    var exp by mutableIntStateOf(0)
    var dayCount by mutableIntStateOf(1)
    var timeOfDay by mutableFloatStateOf(0.2f)

    val inventory = mutableStateMapOf<ItemType, Int>().apply {
        put(ItemType.WOOD_AXE, 1)
        put(ItemType.BERRIES, 8)
        put(ItemType.WOOD, 15)
        put(ItemType.STONE, 8)
    }
    var selectedItem by mutableStateOf<ItemType?>(ItemType.WOOD_AXE)

    val entities = mutableStateListOf<WorldEntity>()
    val popups = mutableStateListOf<DamagePopup>()

    val quests = mutableStateListOf(
        Quest("The Shipwreck Awakening", "Gather 10 Wood & 6 Stone to construct your first campfire.", "Gold + 25, Exp + 50"),
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
        for (i in 0..140) {
            val ex = rng.nextFloat() * 3200f + 200f
            val ey = rng.nextFloat() * 3200f + 200f
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
        val speed = if (stamina > 10f) 6.8f else 4.0f
        playerX = (playerX + deltaX * speed).coerceIn(100f, 3900f)
        playerY = (playerY + deltaY * speed).coerceIn(100f, 3900f)

        hunger = (hunger - 0.005f).coerceAtLeast(0f)
        thirst = (thirst - 0.007f).coerceAtLeast(0f)
        timeOfDay = (timeOfDay + 0.00035f) % 1.0f
        if (timeOfDay > 0.99f) dayCount++

        // Wolf Aggro AI: Wolves chase player when close!
        for (e in entities) {
            if (e.type == "WOLF") {
                val dist = hypot(playerX - e.x, playerY - e.y)
                if (dist in 40f..320f) {
                    val angleToPlayer = atan2(playerY - e.y, playerX - e.x)
                    val wolfSpeed = 2.2f
                    val newX = e.x + cos(angleToPlayer) * wolfSpeed
                    val newY = e.y + sin(angleToPlayer) * wolfSpeed
                    val idx = entities.indexOf(e)
                    if (idx != -1) entities[idx] = e.copy(x = newX, y = newY)
                } else if (dist < 40f) {
                    // Wolf bites player!
                    health = (health - 0.15f).coerceAtLeast(0f)
                }
            }
        }

        // Float up and fade popups
        for (i in popups.indices.reversed()) {
            val p = popups[i]
            p.y -= 2f
            p.alpha -= 0.03f
            if (p.alpha <= 0f) popups.removeAt(i)
        }
    }

    fun interactOrAttack() {
        isAttacking = true
        soundFx?.playSound("SLASH")

        val target = entities.minByOrNull { hypot(it.x - playerX, it.y - playerY) }
        if (target != null && hypot(target.x - playerX, target.y - playerY) < 140f) {
            val dmg = if (selectedItem == ItemType.IRON_SWORD) 35 else if (selectedItem == ItemType.WOOD_AXE) 22 else 12
            target.health -= dmg

            // Sound & Haptics
            when (target.type) {
                "TREE" -> { soundFx?.playSound("CHOP"); soundFx?.vibrate(30) }
                "ROCK" -> { soundFx?.playSound("MINE"); soundFx?.vibrate(40) }
                else -> { soundFx?.playSound("HIT"); soundFx?.vibrate(50) }
            }

            // Damage Popup Number
            addPopup("-$dmg HP", target.x, target.y - 30f, 0xFFFF5252)

            if (target.health <= 0) {
                when (target.type) {
                    "TREE" -> { addItem(ItemType.WOOD, 4); addPopup("+4 Wood 🪵", target.x, target.y, 0xFF81C784) }
                    "ROCK" -> { addItem(ItemType.STONE, 3); addPopup("+3 Stone 🪨", target.x, target.y, 0xFFB0BEC5) }
                    "BERRY_BUSH" -> { addItem(ItemType.BERRIES, 4); addPopup("+4 Berries 🍒", target.x, target.y, 0xFFFF4081) }
                    "WOLF" -> {
                        addItem(ItemType.RAW_MEAT, 2)
                        addPopup("+2 Meat 🥩", target.x, target.y, 0xFFFFAB40)
                        exp += 30
                        if (exp >= 100) {
                            level++
                            exp = 0
                            maxHealth += 20
                            health = maxHealth
                            addPopup("LEVEL UP! 🌟", playerX, playerY - 40f, 0xFFFFD700)
                        }
                    }
                    "CHEST" -> {
                        addItem(ItemType.GOLD_COINS, 25)
                        addItem(ItemType.HEALTH_POTION, 1)
                        soundFx?.playSound("COIN")
                        addPopup("+25 Gold 🪙", target.x, target.y, 0xFFFFD700)
                    }
                }
                entities.remove(target)
            }
        }
    }

    private fun addPopup(text: String, x: Float, y: Float, color: Long) {
        popups.add(DamagePopup(System.currentTimeMillis() + Random.nextLong(1000), text, x, y, color))
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
        soundFx?.vibrate(50)
        exp += 15
        addPopup("Crafted ${recipe.result.displayName}! 🔨", playerX, playerY - 30f, 0xFF64FFDA)
        return true
    }

    fun consumeItem(item: ItemType) {
        val count = inventory[item] ?: return
        when (item) {
            ItemType.BERRIES -> {
                hunger = (hunger + 15f).coerceAtMost(100f)
                health = (health + 5f).coerceAtMost(maxHealth)
                addPopup("+15 Food 🍖", playerX, playerY - 30f, 0xFFFFB74D)
            }
            ItemType.COOKED_MEAT -> {
                hunger = (hunger + 50f).coerceAtMost(100f)
                health = (health + 25f).coerceAtMost(maxHealth)
                addPopup("+50 Food 🍖", playerX, playerY - 30f, 0xFFFFB74D)
            }
            ItemType.HEALTH_POTION -> {
                health = (health + 60f).coerceAtMost(maxHealth)
                addPopup("+60 HP ❤️", playerX, playerY - 30f, 0xFFFF5252)
            }
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

# 2. Update MainActivity to initialize SoundFX
main_code = """package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import com.example.audio.SoundFX
import com.example.engine.GameEngine
import com.example.ui.MainGameScreen

class MainActivity : ComponentActivity() {
    private lateinit var soundFx: SoundFX
    private lateinit var engine: GameEngine

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        soundFx = SoundFX(this)
        engine = GameEngine(soundFx)

        setContent {
            MaterialTheme(colorScheme = darkColorScheme()) {
                Surface(modifier = Modifier.fillMaxSize(), color = Color(0xFF0F1416)) {
                    MainGameScreen(engine = engine)
                }
            }
        }
    }
}
"""

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(main_code)

# 3. Add MiniMap & Floating Popups to MainGameScreen.kt
with open("app/src/main/java/com/example/ui/MainGameScreen.kt", "r") as f:
    mgs = f.read()

# Replace OpenWorldCanvas call to include popup numbers
mgs = mgs.replace(
    "OpenWorldCanvas(engine = engine)",
    "OpenWorldCanvas(engine = engine)\n\n        // Radar Mini-Map (Top Right)\\n        MiniMapRadar(engine = engine, modifier = Modifier.align(Alignment.TopEnd).padding(top = 16.dp, end = 16.dp))"
)

# Move Menu buttons down slightly below MiniMap
mgs = mgs.replace(
    ".padding(16.dp),\\n            horizontalArrangement = Arrangement.spacedBy(8.dp)",
    ".padding(top = 114.dp, end = 16.dp),\\n            horizontalArrangement = Arrangement.spacedBy(8.dp)"
)

with open("app/src/main/java/com/example/ui/MainGameScreen.kt", "w") as f:
    f.write(mgs)

print("GameEngine, MainActivity and MainGameScreen updated with MiniMap and SoundFX!")
