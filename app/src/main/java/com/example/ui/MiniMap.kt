package com.example.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.engine.GameEngine

@Composable
fun MiniMapRadar(
    engine: GameEngine,
    modifier: Modifier = Modifier
) {
    val mapSize = 90.dp
    val radarRadius = 1000f // Visibility radius around player

    Box(
        modifier = modifier
            .size(mapSize)
            .background(Color(0xDD101416), CircleShape)
            .border(2.dp, Color(0xFFFFD54F), CircleShape)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2f, size.height / 2f)
            val radius = size.width / 2f

            // Radar compass background
            drawCircle(Color(0x332E7D32), radius, center)
            drawCircle(Color(0x44FFFFFF), radius * 0.5f, center, style = androidx.compose.ui.graphics.drawscope.Stroke(1f))

            // Draw nearby entities on radar
            for (e in engine.entities) {
                val dx = e.x - engine.playerX
                val dy = e.y - engine.playerY
                val dist = kotlin.math.hypot(dx, dy)
                if (dist < radarRadius) {
                    val mapX = center.x + (dx / radarRadius) * (radius - 8f)
                    val mapY = center.y + (dy / radarRadius) * (radius - 8f)

                    val dotColor = when (e.type) {
                        "WOLF" -> Color.Red
                        "CHEST" -> Color(0xFFFFD54F)
                        "TREE" -> Color(0xFF4CAF50)
                        "ROCK" -> Color.LightGray
                        else -> Color(0xFFE91E63)
                    }
                    drawCircle(dotColor, if (e.type == "WOLF" || e.type == "CHEST") 4f else 2.5f, Offset(mapX, mapY))
                }
            }

            // Player Dot in Center (Glowing Blue)
            drawCircle(Color.White, 5f, center)
            drawCircle(Color(0xFF00E5FF), 3.5f, center)
        }
    }
}
