package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme(colorScheme = darkColorScheme()) {
                Surface(modifier = Modifier.fillMaxSize(), color = Color(0xFF1B2B1B)) {
                    GameView()
                }
            }
        }
    }
}

@Composable
fun GameView() {
    var posX by remember { mutableFloatStateOf(0f) }
    var posY by remember { mutableFloatStateOf(0f) }
    var health by remember { mutableIntStateOf(100) }
    var food by remember { mutableIntStateOf(85) }

    Box(modifier = Modifier.fillMaxSize()) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            drawRect(Color(0xFF233823))
            drawCircle(
                color = Color(0xFFE5A65D),
                radius = 35f,
                center = Offset(center.x + posX, center.y + posY)
            )
        }

        Column(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(20.dp)
                .background(Color(0xCC000000), RoundedCornerShape(10.dp))
                .padding(12.dp)
        ) {
            Text("SURVIVAL RPG", color = Color.White, fontSize = 16.sp)
            Spacer(modifier = Modifier.height(4.dp))
            Text("Health: $health%", color = Color(0xFFFF5252), fontSize = 14.sp)
            Text("Hunger: $food%", color = Color(0xFFFFB142), fontSize = 14.sp)
        }

        Row(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .padding(24.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Button(onClick = { posX -= 20f }) { Text("<") }
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { posY -= 20f }) { Text("^") }
                Button(onClick = { posY += 20f }) { Text("v") }
            }
            Button(onClick = { posX += 20f }) { Text(">") }
        }

        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(24.dp)
                .size(64.dp)
                .background(Color(0xFFD63031), CircleShape)
                .clickable { if (food > 10) food -= 5 },
            contentAlignment = Alignment.Center
        ) {
            Text("ATK", color = Color.White, fontSize = 18.sp)
        }
    }
}
