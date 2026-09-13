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
import kotlin.math.hypot

@Composable
fun MiniMapRadar(
    engine: GameEngine,
    modifier: Modifier = Modifier
) {
    val mapSize = 90.dp
    val radarRadius = 1000f

    Box(
        modifier = modifier
            .size(mapSize)
            .background(Color(0xDD101416), CircleShape)
            .border(2.dp, Color(0xFFFFD54F), CircleShape)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val center = Offset(size.width / 2f, size.height / 2f)
            val radius = size.width / 2f
            val px = engine.rawPlayerX
            val py = engine.rawPlayerY

            drawCircle(Color(0x332E7D32), radius, center)
            drawCircle(Color(0x44FFFFFF), radius * 0.5f, center, style = androidx.compose.ui.graphics.drawscope.Stroke(1f))

            for (e in engine.entities) {
                val dx = e.x - px
                val dy = e.y - py
                val dist = hypot(dx, dy)
                if (dist < radarRadius) {
                    val mapX = center.x + (dx / radarRadius) * (radius - 8f)
                    val mapY = center.y + (dy / radarRadius) * (radius - 8f)

                    val dotColor = when (e.type) {
                        "WOLF", "SKELETON", "BOSS_GOLEM" -> Color.Red
                        "CHEST" -> Color(0xFFFFD54F)
                        "CABIN", "CAMPFIRE" -> Color(0xFF00E676)
                        "TREE" -> Color(0xFF4CAF50)
                        else -> Color.LightGray
                    }
                    drawCircle(dotColor, if (e.type == "BOSS_GOLEM") 5.5f else 3f, Offset(mapX, mapY))
                }
            }

            drawCircle(Color.White, 5f, center)
            drawCircle(Color(0xFF00E5FF), 3.5f, center)
        }
    }
}
