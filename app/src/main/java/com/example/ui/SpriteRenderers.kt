package com.example.ui

import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import kotlin.math.*

// Rich Pixel Tree with layered canopy, bark grain & deep shadow
fun DrawScope.drawHDTree(x: Float, y: Float, isPine: Boolean = false) {
    // 1. Ambient Drop Shadow
    drawOval(
        brush = Brush.radialGradient(
            colors = listOf(Color(0x88000000), Color(0x00000000)),
            center = Offset(x, y + 36f),
            radius = 45f
        ),
        topLeft = Offset(x - 45f, y + 16f),
        size = Size(90f, 40f)
    )

    // 2. Trunk with wood shading
    val trunkBrush = Brush.horizontalGradient(
        colors = listOf(Color(0xFF2E1B0E), Color(0xFF5D4037), Color(0xFF795548), Color(0xFF3E2723)),
        startX = x - 14f,
        endX = x + 14f
    )
    drawRoundRect(
        brush = trunkBrush,
        topLeft = Offset(x - 14f, y - 10f),
        size = Size(28f, 54f),
        cornerRadius = CornerRadius(6f, 6f)
    )
    // Roots
    drawLine(Color(0xFF2E1B0E), Offset(x - 8, y + 36), Offset(x - 22, y + 44), strokeWidth = 5f)
    drawLine(Color(0xFF2E1B0E), Offset(x + 8, y + 36), Offset(x + 22, y + 44), strokeWidth = 5f)

    if (isPine) {
        // Pine Tree tiers
        for (i in 0..2) {
            val tierY = y - 20f - (i * 26f)
            val tierWidth = 70f - (i * 16f)
            val path = Path().apply {
                moveTo(x, tierY - 28f)
                lineTo(x + tierWidth / 2f, tierY)
                lineTo(x - tierWidth / 2f, tierY)
                close()
            }
            drawPath(path, Color(0xFF1B4332))
            drawPath(path, Color(0xFF2D6A4F).copy(alpha = 0.6f), style = Stroke(3f))
        }
    } else {
        // Lush Oak Tree Multi-Canopy
        drawCircle(Color(0xFF14451D), 48f, Offset(x, y - 28f))
        drawCircle(Color(0xFF1E5E2A), 44f, Offset(x - 8f, y - 36f))
        drawCircle(Color(0xFF2D8A3E), 38f, Offset(x + 10f, y - 42f))
        drawCircle(Color(0xFF409A51), 28f, Offset(x - 4f, y - 50f))
        // Highlight spots
        drawCircle(Color(0xFF74C67A).copy(alpha = 0.4f), 12f, Offset(x - 14f, y - 54f))
        drawCircle(Color(0xFF74C67A).copy(alpha = 0.35f), 10f, Offset(x + 12f, y - 36f))
    }
}

// HD Boulder with 3D faceted geometry & mineral ores
fun DrawScope.drawHDRock(x: Float, y: Float, isIron: Boolean = false) {
    // Shadow
    drawOval(Color(0x77000000), Offset(x - 34f, y + 12f), Size(68f, 26f))

    // Base rock facet
    val rockBrush = Brush.linearGradient(
        colors = listOf(Color(0xFF9E9E9E), Color(0xFF616161), Color(0xFF424242)),
        start = Offset(x - 30f, y - 25f),
        end = Offset(x + 30f, y + 25f)
    )
    drawRoundRect(rockBrush, Offset(x - 30f, y - 22f), Size(60f, 44f), CornerRadius(16f, 16f))

    // Rock edge facets
    val highlightFacet = Path().apply {
        moveTo(x - 22f, y - 18f)
        lineTo(x + 8f, y - 22f)
        lineTo(x - 4f, y + 2f)
        close()
    }
    drawPath(highlightFacet, Color(0xFFBDBDBD).copy(alpha = 0.7f))

    // Mineral Ore veins (Glowing Silver Iron or Gold)
    val oreColor = if (isIron) Color(0xFF80D8FF) else Color(0xFFFFD54F)
    drawCircle(oreColor, 5f, Offset(x - 12f, y - 4f))
    drawCircle(oreColor, 4f, Offset(x + 14f, y - 8f))
    drawCircle(oreColor, 6f, Offset(x + 2f, y + 8f))
}

// HD Wild Berry Bush
fun DrawScope.drawHDBush(x: Float, y: Float) {
    drawOval(Color(0x66000000), Offset(x - 28f, y + 8f), Size(56f, 22f))
    drawCircle(Color(0xFF1B5E20), 28f, Offset(x - 10f, y))
    drawCircle(Color(0xFF2E7D32), 30f, Offset(x + 8f, y - 4f))
    drawCircle(Color(0xFF388E3C), 24f, Offset(x, y - 12f))

    // Glossy Red Berries
    val berries = listOf(
        Offset(x - 12f, y - 6f), Offset(x + 14f, y - 8f),
        Offset(x - 4f, y + 6f), Offset(x + 6f, y + 4f),
        Offset(x - 2f, y - 18f)
    )
    for (b in berries) {
        drawCircle(Color(0xFFB71C1C), 6f, b)
        drawCircle(Color(0xFFFF5252), 4f, b + Offset(-1f, -1f))
        drawCircle(Color.White, 1.5f, b + Offset(-2f, -2f))
    }
}

// HD Shadow Beast (Wolf)
fun DrawScope.drawHDWolf(x: Float, y: Float, hp: Int, maxHp: Int) {
    drawOval(Color(0x77000000), Offset(x - 30f, y + 16f), Size(60f, 24f))
    // Body
    drawRoundRect(Color(0xFF263238), Offset(x - 24f, y - 12f), Size(48f, 30f), CornerRadius(10f, 10f))
    // Mane / Fur
    drawCircle(Color(0xFF37474F), 18f, Offset(x - 8f, y - 4f))
    // Head & Ears
    drawCircle(Color(0xFF212121), 16f, Offset(x + 18f, y - 10f))
    val ear1 = Path().apply {
        moveTo(x + 12f, y - 20f); lineTo(x + 18f, y - 32f); lineTo(x + 24f, y - 20f); close()
    }
    drawPath(ear1, Color(0xFF212121))
    // Glowing Red Predator Eyes
    drawCircle(Color(0xFFFF1744), 3.5f, Offset(x + 22f, y - 12f))

    // Monster HP Bar above head
    val barWidth = 48f
    drawRoundRect(Color(0xAA000000), Offset(x - barWidth / 2f, y - 36f), Size(barWidth, 6f), CornerRadius(3f, 3f))
    val fill = (hp.toFloat() / maxHp.toFloat()).coerceIn(0f, 1f)
    drawRoundRect(Color(0xFFFF1744), Offset(x - barWidth / 2f, y - 36f), Size(barWidth * fill, 6f), CornerRadius(3f, 3f))
}

// HD RPG Character with gear, directional view & swing trail
fun DrawScope.drawHDPlayer(
    x: Float,
    y: Float,
    angle: Float,
    isMoving: Boolean,
    isAttacking: Boolean,
    animTick: Float
) {
    // 1. Shadow
    drawOval(
        Color(0x88000000),
        Offset(x - 24f, y + 20f),
        Size(48f, 20f)
    )

    // 2. Walking Bob & Footstep offset
    val walkOffset = if (isMoving) sin(animTick * 8f) * 4f else 0f

    // 3. Knight Cape / Cloak
    drawRoundRect(
        Color(0xFF8E0000),
        Offset(x - 14f, y - 8f + walkOffset),
        Size(28f, 32f),
        CornerRadius(6f, 6f)
    )

    // 4. Steel Plate Armor Body
    val armorBrush = Brush.verticalGradient(
        colors = listOf(Color(0xFFB0BEC5), Color(0xFF546E7A), Color(0xFF37474F)),
        startY = y - 14f + walkOffset,
        endY = y + 18f + walkOffset
    )
    drawRoundRect(
        brush = armorBrush,
        topLeft = Offset(x - 13f, y - 12f + walkOffset),
        size = Size(26f, 28f),
        cornerRadius = CornerRadius(8f, 8f)
    )

    // Gold Guild Emblem on chest
    drawCircle(Color(0xFFFFD54F), 3.5f, Offset(x, y + 2f + walkOffset))

    // 5. Head & Knight Visor Helmet
    drawCircle(Color(0xFFFFCC80), 14f, Offset(x, y - 24f + walkOffset))
    // Helmet
    drawRoundRect(
        Color(0xFF78909C),
        Offset(x - 13f, y - 38f + walkOffset),
        Size(26f, 22f),
        CornerRadius(6f, 6f)
    )
    // Dark Helmet Visor Slit
    drawRoundRect(
        Color(0xFF212121),
        Offset(x - 9f, y - 26f + walkOffset),
        Size(18f, 5f),
        CornerRadius(2f, 2f)
    )
    // Visor eye glint
    drawCircle(Color(0xFF40C4FF), 1.5f, Offset(x - 3f, y - 24f + walkOffset))

    // 6. Weapon & Attack Swing Arc
    val swingAngle = if (isAttacking) angle + sin(animTick * 20f) * 0.8f else angle
    val reach = if (isAttacking) 46f else 24f
    val wx = x + cos(swingAngle) * reach
    val wy = y + sin(swingAngle) * reach + walkOffset

    // Glowing Slash FX when attacking
    if (isAttacking) {
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color(0xAAFFFFFF), Color(0x66FFD54F), Color(0x00FFFFFF)),
                center = Offset(wx, wy),
                radius = 36f
            ),
            radius = 36f,
            center = Offset(wx, wy)
        )
    }

    // Steel Blade
    drawLine(
        color = Color(0xFFECEFF1),
        start = Offset(x + cos(swingAngle) * 8f, y + sin(swingAngle) * 8f + walkOffset),
        end = Offset(wx, wy),
        strokeWidth = 7f
    )
    // Golden Crossguard
    drawCircle(Color(0xFFFFD54F), 4f, Offset(x + cos(swingAngle) * 12f, y + sin(swingAngle) * 12f + walkOffset))
}

// HD Treasure Chest
fun DrawScope.drawPixelChest(x: Float, y: Float) {
    drawOval(Color(0x66000000), Offset(x - 22f, y + 10f), Size(44f, 18f))
    // Chest wooden box
    drawRoundRect(Color(0xFF6D4C41), Offset(x - 20f, y - 16f), Size(40f, 32f), CornerRadius(5f, 5f))
    // Gold straps and lock
    drawRect(Color(0xFFFFD54F), Offset(x - 14f, y - 16f), Size(4f, 32f))
    drawRect(Color(0xFFFFD54F), Offset(x + 10f, y - 16f), Size(4f, 32f))
    drawCircle(Color(0xFFFFD54F), 5f, Offset(x, y - 2f))
    drawCircle(Color(0xFF212121), 2f, Offset(x, y - 2f))
}
