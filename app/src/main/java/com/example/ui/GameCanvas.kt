package com.example.ui

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
    // 60 FPS game tick for smooth wolf chasing and entity updates
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

        // 1. High-Performance Ground Rendering (Large 200px Chunks)
        val tileSize = 200f
        val startTileX = floor((engine.playerX - screenCenterX) / tileSize).toInt() - 1
        val endTileX = ceil((engine.playerX + screenCenterX) / tileSize).toInt() + 1
        val startTileY = floor((engine.playerY - screenCenterY) / tileSize).toInt() - 1
        val endTileY = ceil((engine.playerY + screenCenterY) / tileSize).toInt() + 1

        for (tx in startTileX..endTileX) {
            for (ty in startTileY..endTileY) {
                val worldX = tx * tileSize
                val worldY = ty * tileSize
                val drawX = worldX - engine.playerX + screenCenterX
                val drawY = worldY - engine.playerY + screenCenterY

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

        // 2. High-Performance Entity Rendering with Viewport Culling
        val viewLeft = -100f
        val viewRight = size.width + 100f
        val viewTop = -100f
        val viewBottom = size.height + 100f

        for (e in engine.entities) {
            val drawX = e.x - engine.playerX + screenCenterX
            val drawY = e.y - engine.playerY + screenCenterY

            // Strict Culling: Don't render anything off-screen!
            if (drawX < viewLeft || drawX > viewRight || drawY < viewTop || drawY > viewBottom) continue

            when (e.type) {
                "TREE" -> {
                    // Tree Trunk
                    drawRoundRect(Color(0xFF4A3728), Offset(drawX - 10f, drawY), Size(20f, 40f), CornerRadius(4f, 4f))
                    // Canopy
                    drawCircle(Color(0xFF1B4332), 38f, Offset(drawX, drawY - 24f))
                    drawCircle(Color(0xFF2D6A4F), 28f, Offset(drawX - 4f, drawY - 30f))
                }
                "ROCK" -> {
                    drawRoundRect(Color(0xFF616161), Offset(drawX - 22f, drawY - 14f), Size(44f, 28f), CornerRadius(10f, 10f))
                    drawCircle(Color(0xFFFFD54F), 4f, Offset(drawX - 4f, drawY - 2f)) // Gold ore vein
                }
                "BERRY_BUSH" -> {
                    drawCircle(Color(0xFF2D6A4F), 24f, Offset(drawX, drawY))
                    drawCircle(Color(0xFFE53935), 5f, Offset(drawX - 6f, drawY - 4f))
                    drawCircle(Color(0xFFE53935), 5f, Offset(drawX + 8f, drawY + 2f))
                }
                "WOLF" -> {
                    drawRoundRect(Color(0xFF263238), Offset(drawX - 20f, drawY - 10f), Size(40f, 24f), CornerRadius(6f, 6f))
                    drawCircle(Color(0xFFFF1744), 3f, Offset(drawX + 12f, drawY - 4f))
                    // HP bar
                    val fill = (e.health.toFloat() / e.maxHealth.toFloat()).coerceIn(0f, 1f)
                    drawRect(Color.Red, Offset(drawX - 16f, drawY - 22f), Size(32f * fill, 4f))
                }
                
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

                "CHEST" -> {
                    drawRoundRect(Color(0xFF8D6E63), Offset(drawX - 18f, drawY - 14f), Size(36f, 28f), CornerRadius(4f, 4f))
                    drawRect(Color(0xFFFFD54F), Offset(drawX - 4f, drawY - 2f), Size(8f, 8f))
                }
            }
        }

        // 3. Fast Player Rendering
        // Shadow
        drawOval(Color(0x66000000), Offset(screenCenterX - 20f, screenCenterY + 16f), Size(40f, 16f))
        // Knight Armor Body
        drawRoundRect(Color(0xFF1565C0), Offset(screenCenterX - 13f, screenCenterY - 12f), Size(26f, 26f), CornerRadius(6f, 6f))
        // Helmet
        drawCircle(Color(0xFFFFCC80), 12f, Offset(screenCenterX, screenCenterY - 20f))
        drawRoundRect(Color(0xFF78909C), Offset(screenCenterX - 11f, screenCenterY - 32f), Size(22f, 16f), CornerRadius(4f, 4f))
        drawRect(Color(0xFF212121), Offset(screenCenterX - 7f, screenCenterY - 22f), Size(14f, 4f)) // Visor

        // Weapon
        val reach = if (engine.isAttacking) 38f else 20f
        val wx = screenCenterX + cos(engine.playerAngle) * reach
        val wy = screenCenterY + sin(engine.playerAngle) * reach
        drawLine(
            color = Color(0xFFECEFF1),
            start = Offset(screenCenterX, screenCenterY),
            end = Offset(wx, wy),
            strokeWidth = 6f
        )

        // 4. Smooth Night Lighting Tint
        if (engine.timeOfDay > 0.35f && engine.timeOfDay < 0.85f) {
            drawRect(Color(0x880A0F1D), size = size)
            drawCircle(Color(0x44FFD54F), 180f, Offset(screenCenterX, screenCenterY))
        }

        // Reset attack flag
        if (engine.isAttacking) engine.isAttacking = false
    }
}
