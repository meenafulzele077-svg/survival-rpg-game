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
        // 1. The Living 2D Open World
        OpenWorldCanvas(engine = engine)

        // Radar Mini-Map (Top Right)\n        MiniMapRadar(engine = engine, modifier = Modifier.align(Alignment.TopEnd).padding(top = 16.dp, end = 16.dp))

        // 2. Story Dialogue Overlay
        engine.currentDialog?.let { dialogText ->
            Box(
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .padding(top = 40.dp, start = 16.dp, end = 16.dp)
                    .background(Color(0xEE1B1E24), RoundedCornerShape(12.dp))
                    .border(2.dp, Color(0xFFFFD54F), RoundedCornerShape(12.dp))
                    .padding(16.dp)
                    .clickable { engine.currentDialog = null }
            ) {
                Column {
                    Text("📜 EPISODE I: AWAKENING", color = Color(0xFFFFD54F), fontSize = 13.sp)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(dialogText, color = Color.White, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text("Tap to dismiss", color = Color.Gray, fontSize = 11.sp, modifier = Modifier.align(Alignment.End))
                }
            }
        }

        // 3. Top HUD: Survival Vitals, Time & Level
        Column(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp)
                .background(Color(0xCC11171A), RoundedCornerShape(12.dp))
                .border(1.dp, Color(0xFF2C3E50), RoundedCornerShape(12.dp))
                .padding(12.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("LVL ${engine.level} 🛡️", color = Color.Yellow, fontSize = 15.sp, modifier = Modifier.clickable { showEquipment = true })
                Spacer(modifier = Modifier.width(12.dp))
                Text("🪙 ${engine.gold}", color = Color(0xFFFFD700), fontSize = 14.sp)
                Spacer(modifier = Modifier.width(12.dp))
                Text("☀️ Day ${engine.dayCount}", color = Color.White, fontSize = 13.sp)
            }
            Spacer(modifier = Modifier.height(6.dp))
            StatBar("❤️ HP", engine.health, engine.maxHealth, Color(0xFFE53935))
            StatBar("🍖 Food", engine.hunger, 100f, Color(0xFFFB8C00))
            StatBar("💧 Water", engine.thirst, 100f, Color(0xFF039BE5))
        }

        // 4. Menu Buttons (Crafting & Quests)
        Row(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            IconButton(
                onClick = { showCrafting = true },
                modifier = Modifier.background(Color(0xCC263238), CircleShape)
            ) { Text("🔨", fontSize = 20.sp) }

            IconButton(
                onClick = { showQuests = true },
                modifier = Modifier.background(Color(0xCC263238), CircleShape)
            ) { Text("📜", fontSize = 20.sp) }
        }

        // 5. Virtual Touch Joystick (Bottom Left)
        VirtualJoystick(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .padding(32.dp),
            onMove = { dx, dy ->
                engine.updateJoystick(dx, dy)
            }
        )

        // 6. Action Combat & Interact Button (Bottom Right)
        Box(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(32.dp)
                .size(76.dp)
                .background(Color(0xFFC62828), CircleShape)
                .border(3.dp, Color.White, CircleShape)
                .clickable { engine.interactOrAttack() },
            contentAlignment = Alignment.Center
        ) {
            Text("⚔️", fontSize = 32.sp)
        }

        // 7. Inventory Hotbar (Bottom Center)
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 24.dp)
                .background(Color(0xDD12161A), RoundedCornerShape(16.dp))
                .border(1.dp, Color(0xFF37474F), RoundedCornerShape(16.dp))
                .padding(8.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            engine.inventory.keys.take(5).forEach { item ->
                val isSelected = engine.selectedItem == item
                val count = engine.inventory[item] ?: 0
                Box(
                    modifier = Modifier
                        .size(52.dp)
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

        // Crafting Modal
        
        // Game Over Respawn Modal
        if (engine.isGameOver) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color(0xDD000000)),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("💀 YOU PERISHED", color = Color(0xFFFF1744), fontSize = 28.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("The wilderness of Eldoria overcame you...", color = Color.LightGray, fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(20.dp))
                    Button(
                        onClick = { engine.respawn() },
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
                    ) {
                        Text("Respawn at Camp ⛺", fontSize = 16.sp)
                    }
                }
            }
        }

        if (showCrafting) {
            CraftingDialog(engine = engine, onDismiss = { showCrafting = false })
        }

        // Quest Dialog
        if (showEquipment) {
            EquipmentDialog(engine = engine, onDismiss = { showEquipment = false })
        }
        if (showQuests) {
            QuestDialog(engine = engine, onDismiss = { showQuests = false })
        }
    }
}

@Composable
fun StatBar(label: String, current: Float, max: Float, color: Color) {
    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 2.dp)) {
        Text(label, color = Color.White, fontSize = 11.sp, modifier = Modifier.width(50.dp))
        Box(
            modifier = Modifier
                .width(100.dp)
                .height(8.dp)
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

@Composable
fun CraftingDialog(engine: GameEngine, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = { Button(onClick = onDismiss) { Text("Close") } },
        title = { Text("🔨 Workbench & Crafting", color = Color.White) },
        text = {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(RECIPES) { recipe ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0xFF263238), RoundedCornerShape(8.dp))
                            .padding(10.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("${recipe.result.icon} ${recipe.result.displayName}", color = Color.White)
                            val reqString = recipe.requirements.entries.joinToString(", ") { "${it.key.icon} x${it.value}" }
                            Text(reqString, color = Color.LightGray, fontSize = 12.sp)
                        }
                        Button(
                            onClick = { engine.craft(recipe) },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2E7D32))
                        ) {
                            Text("Craft")
                        }
                    }
                }
            }
        }
    )
}

@Composable
fun QuestDialog(engine: GameEngine, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = { Button(onClick = onDismiss) { Text("Close") } },
        title = { Text("📜 Quest Log: Eldoria", color = Color.White) },
        text = {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                items(engine.quests) { quest ->
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color(0xFF263238), RoundedCornerShape(8.dp))
                            .padding(12.dp)
                    ) {
                        Text(quest.title, color = Color(0xFFFFD54F), fontSize = 15.sp)
                        Text(quest.description, color = Color.White, fontSize = 13.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("Reward: ${quest.reward}", color = Color(0xFF81C784), fontSize = 11.sp)
                    }
                }
            }
        }
    )
}
