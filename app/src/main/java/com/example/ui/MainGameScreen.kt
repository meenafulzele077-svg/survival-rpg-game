package com.example.ui

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
