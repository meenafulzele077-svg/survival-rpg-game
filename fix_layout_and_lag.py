import os

# 1. Update GameEngine to decouple player movement from Compose recomposition
engine_code = """package com.example.engine

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
"""

with open("app/src/main/java/com/example/engine/GameEngine.kt", "w") as f:
    f.write(engine_code)

# 2. Update GameCanvas to read rawPlayer coordinates directly
canvas_code = """package com.example.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import com.example.engine.GameEngine
import kotlin.math.*

@Composable
fun OpenWorldCanvas(engine: GameEngine) {
    // 60 FPS dedicated game loop
    LaunchedEffect(Unit) {
        var lastTime = System.nanoTime()
        while (true) {
            val now = System.nanoTime()
            val dt = (now - lastTime) / 1_000_000_000f
            lastTime = now
            engine.tick(dt.coerceIn(0.01f, 0.05f))
            withFrameNanos { }
        }
    }

    Canvas(modifier = Modifier.fillMaxSize()) {
        val screenCenterX = size.width / 2f
        val screenCenterY = size.height / 2f
        val px = engine.rawPlayerX
        val py = engine.rawPlayerY

        // 1. Ultra Fast Ground Grid
        val tileSize = 200f
        val startTileX = floor((px - screenCenterX) / tileSize).toInt() - 1
        val endTileX = ceil((px + screenCenterX) / tileSize).toInt() + 1
        val startTileY = floor((py - screenCenterY) / tileSize).toInt() - 1
        val endTileY = ceil((py + screenCenterY) / tileSize).toInt() + 1

        for (tx in startTileX..endTileX) {
            for (ty in startTileY..endTileY) {
                val worldX = tx * tileSize
                val worldY = ty * tileSize
                val drawX = worldX - px + screenCenterX
                val drawY = worldY - py + screenCenterY

                val seed = abs(tx * 31 + ty * 17)
                val isWater = seed % 11 == 0
                val isSand = seed % 11 == 1

                val groundColor = when {
                    isWater -> Color(0xFF1E88E5)
                    isSand -> Color(0xFFD4A373)
                    (tx + ty) % 2 == 0 -> Color(0xFF2D6A4F)
                    else -> Color(0xFF1B4332)
                }

                drawRect(
                    color = groundColor,
                    topLeft = Offset(drawX, drawY),
                    size = Size(tileSize + 1f, tileSize + 1f)
                )
            }
        }

        // 2. Render Entities
        val viewLeft = -100f
        val viewRight = size.width + 100f
        val viewTop = -100f
        val viewBottom = size.height + 100f

        for (e in engine.entities) {
            val drawX = e.x - px + screenCenterX
            val drawY = e.y - py + screenCenterY

            if (drawX < viewLeft || drawX > viewRight || drawY < viewTop || drawY > viewBottom) continue

            when (e.type) {
                "TREE" -> {
                    drawRoundRect(Color(0xFF4A3728), Offset(drawX - 10f, drawY), Size(20f, 40f), CornerRadius(4f, 4f))
                    drawCircle(Color(0xFF1B4332), 38f, Offset(drawX, drawY - 24f))
                    drawCircle(Color(0xFF2D6A4F), 28f, Offset(drawX - 4f, drawY - 30f))
                }
                "ROCK" -> {
                    drawRoundRect(Color(0xFF616161), Offset(drawX - 22f, drawY - 14f), Size(44f, 28f), CornerRadius(10f, 10f))
                    drawCircle(Color(0xFFFFD54F), 4f, Offset(drawX - 4f, drawY - 2f))
                }
                "BERRY_BUSH" -> {
                    drawCircle(Color(0xFF2D6A4F), 24f, Offset(drawX, drawY))
                    drawCircle(Color(0xFFE53935), 5f, Offset(drawX - 6f, drawY - 4f))
                    drawCircle(Color(0xFFE53935), 5f, Offset(drawX + 8f, drawY + 2f))
                }
                "WOLF" -> {
                    drawRoundRect(Color(0xFF263238), Offset(drawX - 20f, drawY - 10f), Size(40f, 24f), CornerRadius(6f, 6f))
                    drawCircle(Color(0xFFFF1744), 3f, Offset(drawX + 12f, drawY - 4f))
                    val fill = (e.health.toFloat() / e.maxHealth.toFloat()).coerceIn(0f, 1f)
                    drawRect(Color.Red, Offset(drawX - 16f, drawY - 22f), Size(32f * fill, 4f))
                }
                "SKELETON" -> {
                    drawCircle(Color(0xFFE0E0E0), 10f, Offset(drawX, drawY - 18f))
                    drawRoundRect(Color(0xFFBDBDBD), Offset(drawX - 10f, drawY - 8f), Size(20f, 24f), CornerRadius(4f, 4f))
                    val fill = (e.health.toFloat() / e.maxHealth.toFloat()).coerceIn(0f, 1f)
                    drawRect(Color.Red, Offset(drawX - 15f, drawY - 30f), Size(30f * fill, 3f))
                }
                "BOSS_GOLEM" -> {
                    drawOval(Color(0x77000000), Offset(drawX - 45f, drawY + 28f), Size(90f, 30f))
                    drawRoundRect(Color(0xFF455A64), Offset(drawX - 35f, drawY - 35f), Size(70f, 65f), CornerRadius(16f, 16f))
                    drawCircle(Color(0xFF00E5FF), 5f, Offset(drawX - 12f, drawY - 15f))
                    drawCircle(Color(0xFF00E5FF), 5f, Offset(drawX + 12f, drawY - 15f))
                    val fill = (e.health.toFloat() / e.maxHealth.toFloat()).coerceIn(0f, 1f)
                    drawRect(Color.Red, Offset(drawX - 50f, drawY - 55f), Size(100f * fill, 8f))
                }
                "CAMPFIRE" -> {
                    drawCircle(Color(0xFF424242), 22f, Offset(drawX, drawY + 4f))
                    drawCircle(Color(0xFFFF9800), 16f, Offset(drawX, drawY - 2f))
                    drawCircle(Color(0xFFFFEB3B), 9f, Offset(drawX, drawY - 4f))
                }
                "CABIN" -> {
                    drawRoundRect(Color(0xFF5D4037), Offset(drawX - 35f, drawY - 25f), Size(70f, 50f), CornerRadius(8f, 8f))
                    drawRoundRect(Color(0xFF795548), Offset(drawX - 30f, drawY - 45f), Size(60f, 25f), CornerRadius(6f, 6f))
                    drawRect(Color(0xFF2E1B0E), Offset(drawX - 10f, drawY), Size(20f, 25f))
                }
                "CHEST" -> {
                    drawRoundRect(Color(0xFF8D6E63), Offset(drawX - 18f, drawY - 14f), Size(36f, 28f), CornerRadius(4f, 4f))
                    drawRect(Color(0xFFFFD54F), Offset(drawX - 4f, drawY - 2f), Size(8f, 8f))
                }
            }
        }

        // 3. Fast Player Rendering
        drawOval(Color(0x66000000), Offset(screenCenterX - 20f, screenCenterY + 16f), Size(40f, 16f))
        drawRoundRect(Color(0xFF1565C0), Offset(screenCenterX - 13f, screenCenterY - 12f), Size(26f, 26f), CornerRadius(6f, 6f))
        drawCircle(Color(0xFFFFCC80), 12f, Offset(screenCenterX, screenCenterY - 20f))
        drawRoundRect(Color(0xFF78909C), Offset(screenCenterX - 11f, screenCenterY - 32f), Size(22f, 16f), CornerRadius(4f, 4f))
        drawRect(Color(0xFF212121), Offset(screenCenterX - 7f, screenCenterY - 22f), Size(14f, 4f))

        val reach = if (engine.rawIsAttacking) 38f else 20f
        val wx = screenCenterX + cos(engine.rawAngle) * reach
        val wy = screenCenterY + sin(engine.rawAngle) * reach
        drawLine(
            color = Color(0xFFECEFF1),
            start = Offset(screenCenterX, screenCenterY),
            end = Offset(wx, wy),
            strokeWidth = 6f
        )

        // 4. Night Tint
        if (engine.timeOfDay > 0.35f && engine.timeOfDay < 0.85f) {
            drawRect(Color(0x880A0F1D), size = size)
            drawCircle(Color(0x44FFD54F), 180f, Offset(screenCenterX, screenCenterY))
        }

        if (engine.rawIsAttacking) engine.rawIsAttacking = false
    }
}
"""

with open("app/src/main/java/com/example/ui/GameCanvas.kt", "w") as f:
    f.write(canvas_code)

# 3. Completely Overhaul MainGameScreen Layout (Clean Non-Overlapping Thumb Controls)
screen_code = """package com.example.ui

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
    var showEquipment by remember { mutableStateOf(false) }

    Box(modifier = Modifier.fillMaxSize()) {
        // 1. Smooth 60 FPS Canvas
        OpenWorldCanvas(engine = engine)

        // 2. Top-Left HUD (Vitals & Level) - Clean & Pinned
        Column(
            modifier = Modifier
                .align(Alignment.TopStart)
                .statusBarsPadding()
                .padding(12.dp)
                .background(Color(0xDD11171A), RoundedCornerShape(12.dp))
                .border(1.dp, Color(0xFF2C3E50), RoundedCornerShape(12.dp))
                .padding(10.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "LVL ${engine.level} 🛡️",
                    color = Color.Yellow,
                    fontSize = 14.sp,
                    modifier = Modifier.clickable { showEquipment = true }
                )
                Spacer(modifier = Modifier.width(10.dp))
                Text("🪙 ${engine.gold}", color = Color(0xFFFFD700), fontSize = 13.sp)
                Spacer(modifier = Modifier.width(10.dp))
                Text("☀️ Day ${engine.dayCount}", color = Color.White, fontSize = 12.sp)
            }
            Spacer(modifier = Modifier.height(4.dp))
            StatBar("❤️ HP", engine.health, engine.maxHealth, Color(0xFFE53935))
            StatBar("🍖 Food", engine.hunger, 100f, Color(0xFFFB8C00))
            StatBar("💧 Water", engine.thirst, 100f, Color(0xFF039BE5))
        }

        // 3. Top-Right MiniMap & Menu Row
        Column(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .statusBarsPadding()
                .padding(12.dp),
            horizontalAlignment = Alignment.End
        ) {
            MiniMapRadar(engine = engine)
            Spacer(modifier = Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                IconButton(
                    onClick = { showCrafting = true },
                    modifier = Modifier.size(44.dp).background(Color(0xDD263238), CircleShape)
                ) { Text("🔨", fontSize = 18.sp) }

                IconButton(
                    onClick = { showQuests = true },
                    modifier = Modifier.size(44.dp).background(Color(0xDD263238), CircleShape)
                ) { Text("📜", fontSize = 18.sp) }
            }
        }

        // 4. Story Dialogue - Positioned nicely in the middle without covering stats!
        engine.currentDialog?.let { dialogText ->
            Box(
                modifier = Modifier
                    .align(Alignment.Center)
                    .padding(horizontal = 24.dp)
                    .background(Color(0xF0181F26), RoundedCornerShape(14.dp))
                    .border(2.dp, Color(0xFFFFD54F), RoundedCornerShape(14.dp))
                    .padding(16.dp)
                    .clickable { engine.currentDialog = null }
            ) {
                Column {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("📜 CHRONICLES OF ELDORIA", color = Color(0xFFFFD54F), fontSize = 13.sp)
                        Text("✕ Tap to Close", color = Color.LightGray, fontSize = 11.sp)
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(dialogText, color = Color.White, fontSize = 14.sp)
                }
            }
        }

        // 5. Controls Section (Bottom)
        // Analog Joystick (Comfortable Lower-Left)
        VirtualJoystick(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .navigationBarsPadding()
                .padding(start = 24.dp, bottom = 90.dp),
            onMove = { dx, dy -> engine.updateJoystick(dx, dy) }
        )

        // Action / Attack Button (Spacious Lower-Right)
        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .navigationBarsPadding()
                .padding(end = 24.dp, bottom = 90.dp)
                .size(76.dp)
                .background(Color(0xFFD32F2F), CircleShape)
                .border(3.dp, Color.White, CircleShape)
                .clickable { engine.interactOrAttack() },
            contentAlignment = Alignment.Center
        ) {
            Text("⚔️", fontSize = 34.sp)
        }

        // 6. Centered Inventory Hotbar (Pinned to Bottom Center)
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .navigationBarsPadding()
                .padding(bottom = 12.dp)
                .background(Color(0xEE12161A), RoundedCornerShape(14.dp))
                .border(1.dp, Color(0xFF37474F), RoundedCornerShape(14.dp))
                .padding(horizontal = 10.dp, vertical = 6.dp),
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            engine.inventory.keys.take(5).forEach { item ->
                val isSelected = engine.selectedItem == item
                val count = engine.inventory[item] ?: 0
                Box(
                    modifier = Modifier
                        .size(50.dp)
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
                            } else if (item.category == "Building") {
                                engine.placeBuilding(item)
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

        // Game Over Respawn Modal
        if (engine.isGameOver) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color(0xDD000000)),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("💀 YOU PERISHED", color = Color(0xFFFF1744), fontSize = 26.sp)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text("The wilderness of Eldoria overcame you...", color = Color.LightGray, fontSize = 13.sp)
                    Spacer(modifier = Modifier.height(18.dp))
                    Button(
                        onClick = { engine.respawn() },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
                    ) {
                        Text("Respawn at Camp ⛺", fontSize = 15.sp)
                    }
                }
            }
        }

        if (showEquipment) {
            EquipmentDialog(engine = engine, onDismiss = { showEquipment = false })
        }
        if (showCrafting) {
            CraftingDialog(engine = engine, onDismiss = { showCrafting = false })
        }
        if (showQuests) {
            QuestDialog(engine = engine, onDismiss = { showQuests = false })
        }
    }
}

@Composable
fun StatBar(label: String, current: Float, max: Float, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 2.dp)) {
        Text(label, color = Color.White, fontSize = 11.sp, modifier = Modifier.width(46.dp))
        Box(
            modifier = Modifier
                .width(90.dp)
                .height(7.dp)
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
"""

with open("app/src/main/java/com/example/ui/MainGameScreen.kt", "w") as f:
    f.write(screen_code)

print("PERFORMANCE & LAYOUT OVERHAUL COMPLETE!")
