content = """package com.example.ui

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import com.example.engine.GameEngine
import kotlin.math.*

@Composable
fun OpenWorldCanvas(engine: GameEngine) {
    val infiniteTransition = rememberInfiniteTransition(label = "worldAnim")
    val animTick by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 6.2831f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "tick"
    )

    Canvas(modifier = Modifier.fillMaxSize()) {
        val screenCenterX = size.width / 2f
        val screenCenterY = size.height / 2f

        // 1. Procedural High-Detail Terrain Grid
        val tileSize = 128f
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
                val isWater = seed % 13 == 0
                val isSand = seed % 13 == 1
                val isPath = (tx % 8 == 0) || (ty % 14 == 0)

                if (isWater) {
                    // Deep ocean with animated shore wave ripples
                    val wavePulse = sin(animTick + tx) * 3f
                    drawRect(
                        brush = Brush.verticalGradient(
                            colors = listOf(Color(0xFF1976D2), Color(0xFF0D47A1)),
                            startY = drawY,
                            endY = drawY + tileSize
                        ),
                        topLeft = Offset(drawX, drawY),
                        size = Size(tileSize + 1f, tileSize + 1f)
                    )
                    // Water foam line
                    drawLine(
                        color = Color(0x66FFFFFF),
                        start = Offset(drawX, drawY + tileSize / 2f + wavePulse),
                        end = Offset(drawX + tileSize, drawY + tileSize / 2f - wavePulse),
                        strokeWidth = 3f
                    )
                } else if (isSand) {
                    drawRect(
                        color = Color(0xFFDEB887),
                        topLeft = Offset(drawX, drawY),
                        size = Size(tileSize + 1f, tileSize + 1f)
                    )
                } else if (isPath) {
                    // Cobblestone / Dirt Trail
                    drawRect(
                        color = Color(0xFF6D4C41),
                        topLeft = Offset(drawX, drawY),
                        size = Size(tileSize + 1f, tileSize + 1f)
                    )
                    drawCircle(Color(0xFF8D6E63), 6f, Offset(drawX + 32f, drawY + 40f))
                    drawCircle(Color(0xFF5D4037), 8f, Offset(drawX + 80f, drawY + 70f))
                } else {
                    // Lush Grass Tile with wild flower accents
                    val grassBase = if ((tx + ty) % 2 == 0) Color(0xFF2E7D32) else Color(0xFF388E3C)
                    drawRect(
                        color = grassBase,
                        topLeft = Offset(drawX, drawY),
                        size = Size(tileSize + 1f, tileSize + 1f)
                    )
                    // Little flower dots
                    if (seed % 5 == 0) {
                        drawCircle(Color(0xFFFFEB3B), 3f, Offset(drawX + 28f, drawY + 36f))
                    } else if (seed % 7 == 0) {
                        drawCircle(Color(0xFFE91E63), 3f, Offset(drawX + 84f, drawY + 88f))
                    }
                }
            }
        }

        // 2. Render all Living Entities sorted by Y (for 2.5D Isometric depth)
        val sortedEntities = engine.entities.sortedBy { it.y }
        for (e in sortedEntities) {
            val drawX = e.x - engine.playerX + screenCenterX
            val drawY = e.y - engine.playerY + screenCenterY

            // Off-screen culling
            if (drawX < -150 || drawX > size.width + 150 || drawY < -150 || drawY > size.height + 150) continue

            when (e.type) {
                "TREE" -> drawHDTree(drawX, drawY, isPine = (e.id % 2 == 0))
                "ROCK" -> drawHDRock(drawX, drawY, isIron = (e.id % 3 == 0))
                "BERRY_BUSH" -> drawHDBush(drawX, drawY)
                "WOLF" -> drawHDWolf(drawX, drawY, e.health, e.maxHealth)
                "CHEST" -> {
                    drawPixelChest(drawX, drawY)
                }
            }
        }

        // 3. Render High-Detail Player in Center
        drawHDPlayer(
            x = screenCenterX,
            y = screenCenterY,
            angle = engine.playerAngle,
            isMoving = engine.isMoving,
            isAttacking = engine.isAttacking,
            animTick = animTick
        )

        // Reset attack swing after rendering
        if (engine.isAttacking) {
            engine.isAttacking = false
        }

        // 4. Dramatic Atmospheric Lighting (Day / Sunset / Midnight)
        val ambientNightAlpha = when {
            engine.timeOfDay in 0.0f..0.25f -> 0.0f
            engine.timeOfDay in 0.25f..0.38f -> (engine.timeOfDay - 0.25f) / 0.13f * 0.72f // Sunset
            engine.timeOfDay in 0.38f..0.85f -> 0.78f // Deep Starry Night
            else -> (1.0f - engine.timeOfDay) / 0.15f * 0.78f // Sunrise
        }

        if (ambientNightAlpha > 0.05f) {
            drawRect(
                color = Color(0xFF0A0F1D).copy(alpha = ambientNightAlpha),
                size = size
            )
            // Player Warm Torchlight Radiance
            drawCircle(
                brush = Brush.radialGradient(
                    colors = listOf(Color(0xFFFFD54F).copy(alpha = 0.45f), Color(0x00FFD54F)),
                    center = Offset(screenCenterX, screenCenterY),
                    radius = 240f
                ),
                radius = 240f,
                center = Offset(screenCenterX, screenCenterY)
            )
        }
    }
}
"""

with open("app/src/main/java/com/example/ui/GameCanvas.kt", "w") as f:
    f.write(content)
print("GameCanvas updated with HD sprites and atmospheric shaders!")
