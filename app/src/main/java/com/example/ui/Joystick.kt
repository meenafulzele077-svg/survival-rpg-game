package com.example.ui

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
