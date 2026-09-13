package com.example.ui

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
