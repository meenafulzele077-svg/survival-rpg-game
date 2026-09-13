import os

files = {
    "app/src/main/java/com/example/model/GameData.kt": """package com.example.model

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
""",

    "app/src/main/java/com/example/engine/GameEngine.kt": """package com.example.engine

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
""",

    "app/src/main/java/com/example/ui/Joystick.kt": """package com.example.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import kotlin.math.*

@Composable
fun VirtualJoystick(
    modifier: Modifier = Modifier,
    onMove: (Float, Float) -> Unit
) {
    var knobPosition by remember { mutableStateOf(Offset.Zero) }
    val maxRadius = 100f

    Box(
        modifier = modifier
            .size(140.dp)
            .pointerInput(Unit) {
                detectDragGestures(
                    onDragStart = { offset ->
                        val center = Offset(size.width / 2f, size.height / 2f)
                        val dragVector = offset - center
                        val dist = dragVector.getDistance().coerceAtMost(maxRadius)
                        val angle = atan2(dragVector.y, dragVector.x)
                        knobPosition = Offset(cos(angle) * dist, sin(angle) * dist)
                        onMove(knobPosition.x / maxRadius, knobPosition.y / maxRadius)
                    },
                    onDrag = { change, _ ->
                        change.consume()
                        val center = Offset(size.width / 2f, size.height / 2f)
                        val dragVector = change.position - center
                        val dist = dragVector.getDistance().coerceAtMost(maxRadius)
                        val angle = atan2(dragVector.y, dragVector.x)
                        knobPosition = Offset(cos(angle) * dist, sin(angle) * dist)
                        onMove(knobPosition.x / maxRadius, knobPosition.y / maxRadius)
                    },
                    onDragEnd = {
                        knobPosition = Offset.Zero
                        onMove(0f, 0f)
                    },
                    onDragCancel = {
                        knobPosition = Offset.Zero
                        onMove(0f, 0f)
                    }
                )
            }
    ) {
        Canvas(modifier = Modifier.matchParentSize()) {
            val center = Offset(size.width / 2f, size.height / 2f)
            // Outer Ring
            drawCircle(
                color = Color(0x66000000),
                radius = maxRadius,
                center = center
            )
            drawCircle(
                color = Color(0xAAFFFFFF),
                radius = maxRadius,
                center = center,
                style = androidx.compose.ui.graphics.drawscope.Stroke(width = 3f)
            )
            // Knob
            drawCircle(
                color = Color(0xFF4CAF50),
                radius = 35f,
                center = center + knobPosition
            )
        }
    }
}
""",

    "app/src/main/java/com/example/ui/GameCanvas.kt": """package com.example.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import com.example.engine.GameEngine
import kotlin.math.*

@Composable
fun OpenWorldCanvas(engine: GameEngine) {
    Canvas(modifier = Modifier.fillMaxSize()) {
        val screenCenterX = size.width / 2f
        val screenCenterY = size.height / 2f

        // 1. Draw procedural tile ground
        val tileSize = 120f
        val startTileX = floor((engine.playerX - screenCenterX) / tileSize).toInt()
        val endTileX = ceil((engine.playerX + screenCenterX) / tileSize).toInt()
        val startTileY = floor((engine.playerY - screenCenterY) / tileSize).toInt()
        val endTileY = ceil((engine.playerY + screenCenterY) / tileSize).toInt()

        for (tx in startTileX..endTileX) {
            for (ty in startTileY..endTileY) {
                val worldX = tx * tileSize
                val worldY = ty * tileSize
                val drawX = worldX - engine.playerX + screenCenterX
                val drawY = worldY - engine.playerY + screenCenterY

                val isWater = (tx + ty) % 11 == 0
                val isDirt = (tx * 7 + ty * 3) % 9 == 0
                val tileColor = when {
                    isWater -> Color(0xFF2E6F9E)
                    isDirt -> Color(0xFF5D4037)
                    (tx + ty) % 2 == 0 -> Color(0xFF386629)
                    else -> Color(0xFF2F5422)
                }

                drawRect(
                    color = tileColor,
                    topLeft = Offset(drawX, drawY),
                    size = Size(tileSize + 1f, tileSize + 1f)
                )
            }
        }

        // 2. Draw Entities (Trees, Rocks, Mobs, Chests)
        for (e in engine.entities) {
            val drawX = e.x - engine.playerX + screenCenterX
            val drawY = e.y - engine.playerY + screenCenterY

            // Culling off-screen entities
            if (drawX < -100 || drawX > size.width + 100 || drawY < -100 || drawY > size.height + 100) continue

            when (e.type) {
                "TREE" -> drawPixelTree(drawX, drawY)
                "ROCK" -> drawPixelRock(drawX, drawY)
                "BERRY_BUSH" -> drawPixelBush(drawX, drawY)
                "WOLF" -> drawPixelWolf(drawX, drawY, e.health)
                "CHEST" -> drawPixelChest(drawX, drawY)
            }
        }

        // 3. Draw Player in Center with Pixel details
        drawPixelPlayer(screenCenterX, screenCenterY, engine.playerAngle, engine.isAttacking)

        // 4. Day / Night ambient tint
        val nightAlpha = when {
            engine.timeOfDay < 0.25f -> 0.0f
            engine.timeOfDay in 0.25f..0.35f -> (engine.timeOfDay - 0.25f) * 6f * 0.7f // Dusk
            engine.timeOfDay in 0.35f..0.85f -> 0.75f // Night
            else -> (1.0f - engine.timeOfDay) * 5f * 0.75f // Dawn
        }
        if (nightAlpha > 0.05f) {
            drawRect(
                color = Color(0xFF070B19).copy(alpha = nightAlpha),
                size = size
            )
            // Player Torch Light in Night
            drawCircle(
                color = Color(0xFFFFD54F).copy(alpha = 0.25f),
                radius = 180f,
                center = Offset(screenCenterX, screenCenterY)
            )
        }
    }
}

fun DrawScope.drawPixelTree(x: Float, y: Float) {
    // Shadow
    drawOval(Color(0x55000000), Offset(x - 30, y + 25), Size(60f, 25f))
    // Trunk
    drawRoundRect(Color(0xFF4E342E), Offset(x - 12, y), Size(24f, 45f), CornerRadius(4f, 4f))
    // Foliage
    drawCircle(Color(0xFF1B5E20), 42f, Offset(x, y - 25))
    drawCircle(Color(0xFF2E7D32), 34f, Offset(x - 6, y - 32))
    drawCircle(Color(0xFF43A047), 20f, Offset(x + 10, y - 38))
}

fun DrawScope.drawPixelRock(x: Float, y: Float) {
    drawOval(Color(0x55000000), Offset(x - 25, y + 10), Size(50f, 20f))
    drawRoundRect(Color(0xFF616161), Offset(x - 22, y - 15), Size(44f, 32f), CornerRadius(10f, 10f))
    drawRoundRect(Color(0xFF9E9E9E), Offset(x - 16, y - 10), Size(20f, 14f), CornerRadius(5f, 5f))
}

fun DrawScope.drawPixelBush(x: Float, y: Float) {
    drawCircle(Color(0xFF2E7D32), 26f, Offset(x, y))
    drawCircle(Color(0xFFD32F2F), 5f, Offset(x - 8, y - 6))
    drawCircle(Color(0xFFD32F2F), 5f, Offset(x + 7, y + 4))
}

fun DrawScope.drawPixelWolf(x: Float, y: Float, hp: Int) {
    drawOval(Color(0x55000000), Offset(x - 20, y + 12), Size(40f, 16f))
    drawRoundRect(Color(0xFF424242), Offset(x - 18, y - 10), Size(36f, 24f), CornerRadius(6f, 6f))
    // Eyes
    drawCircle(Color(0xFFFF1744), 3f, Offset(x + 8, y - 4))
    // Health bar
    drawRect(Color.Red, Offset(x - 18, y - 20), Size(36f * (hp / 80f), 4f))
}

fun DrawScope.drawPixelChest(x: Float, y: Float) {
    drawRoundRect(Color(0xFF8D6E63), Offset(x - 18, y - 14), Size(36f, 28f), CornerRadius(4f, 4f))
    drawRect(Color(0xFFFFD54F), Offset(x - 4, y - 2), Size(8f, 8f))
}

fun DrawScope.drawPixelPlayer(x: Float, y: Float, angle: Float, isAttacking: Boolean) {
    // Shadow
    drawOval(Color(0x55000000), Offset(x - 20, y + 18), Size(40f, 16f))
    // Body (Armor)
    drawRoundRect(Color(0xFF1565C0), Offset(x - 15, y - 10), Size(30f, 32f), CornerRadius(6f, 6f))
    // Head & Helmet
    drawCircle(Color(0xFFFFCC80), 16f, Offset(x, y - 22))
    drawRoundRect(Color(0xFF78909C), Offset(x - 15, y - 36), Size(30f, 16f), CornerRadius(4f, 4f))

    // Weapon Swing
    val weaponReach = if (isAttacking) 35f else 18f
    val wx = x + cos(angle) * weaponReach
    val wy = y + sin(angle) * weaponReach
    drawLine(
        color = Color(0xFFCFD8DC),
        start = Offset(x, y),
        end = Offset(wx, wy),
        strokeWidth = 6f
    )
}
""",

    "app/src/main/java/com/example/ui/MainGameScreen.kt": """package com.example.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.engine.GameEngine
import com.example.model.*

@Composable
fun MainGameScreen(engine: GameEngine) {
    var showCrafting by remember { mutableStateOf(false) }
    var showQuests by remember { mutableStateOf(false) }

    Box(modifier = Modifier.fillMaxSize()) {
        // 1. The Living 2D Open World
        OpenWorldCanvas(engine = engine)

        // 2. Story Dialogue Overlay
        engine.currentDialog?.let { dialogText ->
            Box(
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(top = 40.dp, start = 16.dp, end = 16.dp)
                    .background(Color(0xEE1B1E24), RoundedCornerShape(12.dp))
                    .border(2.dp, Color(0xFFFFD54F), RoundedCornerShape(12.dp))
                    .padding(16.dp)
                    .clickable { engine.currentDialog = null }
            ) {
                Column {
                    Text("📜 EPISODE I: AWAKENING", color = Color(0xFFFFD54F), fontSize = 13.sp)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(dialogText, color = Color.White, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text("Tap to dismiss", color = Color.Gray, fontSize = 11.sp, modifier = Modifier.align(Alignment.End))
                }
            }
        }

        // 3. Top HUD: Survival Vitals, Time & Level
        Column(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp)
                .background(Color(0xCC11171A), RoundedCornerShape(12.dp))
                .border(1.dp, Color(0xFF2C3E50), RoundedCornerShape(12.dp))
                .padding(12.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("LVL ${engine.level}", color = Color.Yellow, fontSize = 15.sp)
                Spacer(modifier = Modifier.width(12.dp))
                Text("🪙 ${engine.gold}", color = Color(0xFFFFD700), fontSize = 14.sp)
                Spacer(modifier = Modifier.width(12.dp))
                Text("☀️ Day ${engine.dayCount}", color = Color.White, fontSize = 13.sp)
            }
            Spacer(modifier = Modifier.height(6.dp))
            StatBar("❤️ HP", engine.health, engine.maxHealth, Color(0xFFE53935))
            StatBar("🍖 Food", engine.hunger, 100f, Color(0xFFFB8C00))
            StatBar("💧 Water", engine.thirst, 100f, Color(0xFF039BE5))
        }

        // 4. Menu Buttons (Crafting & Quests)
        Row(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            IconButton(
                onClick = { showCrafting = true },
                modifier = Modifier.background(Color(0xCC263238), CircleShape)
            ) { Text("🔨", fontSize = 20.sp) }

            IconButton(
                onClick = { showQuests = true },
                modifier = Modifier.background(Color(0xCC263238), CircleShape)
            ) { Text("📜", fontSize = 20.sp) }
        }

        // 5. Virtual Touch Joystick (Bottom Left)
        VirtualJoystick(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .padding(32.dp),
            onMove = { dx, dy ->
                engine.updateJoystick(dx, dy)
            }
        )

        // 6. Action Combat & Interact Button (Bottom Right)
        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(32.dp)
                .size(76.dp)
                .background(Color(0xFFC62828), CircleShape)
                .border(3.dp, Color.White, CircleShape)
                .clickable { engine.interactOrAttack() },
            contentAlignment = Alignment.Center
        ) {
            Text("⚔️", fontSize = 32.sp)
        }

        // 7. Inventory Hotbar (Bottom Center)
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 24.dp)
                .background(Color(0xDD12161A), RoundedCornerShape(16.dp))
                .border(1.dp, Color(0xFF37474F), RoundedCornerShape(16.dp))
                .padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            engine.inventory.keys.take(5).forEach { item ->
                val isSelected = engine.selectedItem == item
                val count = engine.inventory[item] ?: 0
                Box(
                    modifier = Modifier
                        .size(52.dp)
                        .background(
                            if (isSelected) Color(0xFF2E7D32) else Color(0xFF1E262C),
                            RoundedCornerShape(10.dp)
                        )
                        .border(
                            2.dp,
                            if (isSelected) Color.Yellow else Color.Transparent,
                            RoundedCornerShape(10.dp)
                        )
                        .clickable {
                            engine.selectedItem = item
                            if (item.category == "Food" || item.category == "Consumable") {
                                engine.consumeItem(item)
                            }
                        },
                    contentAlignment = Alignment.Center
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(item.icon, fontSize = 20.sp)
                        Text("x$count", fontSize = 10.sp, color = Color.White)
                    }
                }
            }
        }

        // Crafting Modal
        if (showCrafting) {
            CraftingDialog(engine = engine, onDismiss = { showCrafting = false })
        }

        // Quest Dialog
        if (showQuests) {
            QuestDialog(engine = engine, onDismiss = { showQuests = false })
        }
    }
}

@Composable
fun StatBar(label: String, current: Float, max: Float, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 2.dp)) {
        Text(label, color = Color.White, fontSize = 11.sp, modifier = Modifier.width(50.dp))
        Box(
            modifier = Modifier
                .width(100.dp)
                .height(8.dp)
                .background(Color(0x55000000), RoundedCornerShape(4.dp))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth((current / max).coerceIn(0f, 1f))
                    .background(color, RoundedCornerShape(4.dp))
            )
        }
    }
}

@Composable
fun CraftingDialog(engine: GameEngine, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = { Button(onClick = onDismiss) { Text("Close") } },
        title = { Text("🔨 Workbench & Crafting", color = Color.White) },
        text = {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(RECIPES) { recipe ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0xFF263238), RoundedCornerShape(8.dp))
                            .padding(10.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("${recipe.result.icon} ${recipe.result.displayName}", color = Color.White)
                            val reqString = recipe.requirements.entries.joinToString(", ") { "${it.key.icon} x${it.value}" }
                            Text(reqString, color = Color.LightGray, fontSize = 12.sp)
                        }
                        Button(
                            onClick = { engine.craft(recipe) },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
                        ) {
                            Text("Craft")
                        }
                    }
                }
            }
        }
    )
}

@Composable
fun QuestDialog(engine: GameEngine, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = { Button(onClick = onDismiss) { Text("Close") } },
        title = { Text("📜 Quest Log: Eldoria", color = Color.White) },
        text = {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                items(engine.quests) { quest ->
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0xFF263238), RoundedCornerShape(8.dp))
                            .padding(12.dp)
                    ) {
                        Text(quest.title, color = Color(0xFFFFD54F), fontSize = 15.sp)
                        Text(quest.description, color = Color.White, fontSize = 13.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("Reward: ${quest.reward}", color = Color(0xFF81C784), fontSize = 11.sp)
                    }
                }
            }
        }
    )
}
""",

    "app/src/main/java/com/example/MainActivity.kt": """package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import com.example.engine.GameEngine
import com.example.ui.MainGameScreen

class MainActivity : ComponentActivity() {
    private val engine = GameEngine()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
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
}

for path, content in files.items():
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"Generated: {path}")

print("✨ COMPLETE SURVIVAL RPG CODEBASE GENERATED SUCCESSFULLY!")
