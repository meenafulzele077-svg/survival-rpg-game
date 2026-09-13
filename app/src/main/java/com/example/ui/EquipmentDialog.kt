package com.example.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.engine.GameEngine

@Composable
fun EquipmentDialog(engine: GameEngine, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = { Button(onClick = onDismiss) { Text("Close") } },
        title = { Text("🛡️ Hero Equipment & Stats", color = Color(0xFFFFD54F)) },
        text = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1B2228), RoundedCornerShape(12.dp))
                    .padding(16.dp)
            ) {
                Text("Knight of Eldoria - Level ${engine.level}", color = Color.White, fontSize = 16.sp)
                Spacer(modifier = Modifier.height(10.dp))

                EquipmentSlot("🗡️ Weapon", engine.selectedItem?.displayName ?: "Fists")
                EquipmentSlot("🛡️ Armor", "Tempered Plate (+15 Def)")
                EquipmentSlot("⛑️ Helmet", "Iron Visor (+10 Def)")
                EquipmentSlot("🎒 Pack", "${engine.inventory.size}/20 Slots Used")

                Spacer(modifier = Modifier.height(12.dp))
                HorizontalDivider(color = Color(0xFF37474F))
                Spacer(modifier = Modifier.height(8.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Total Attack: ${if (engine.selectedItem?.name == "EXCALIBUR") 85 else 25}", color = Color(0xFFFF8A80), fontSize = 13.sp)
                    Text("Total Gold: 🪙 ${engine.gold}", color = Color(0xFFFFD700), fontSize = 13.sp)
                }
            }
        }
    )
}

@Composable
fun EquipmentSlot(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
            .background(Color(0xFF263238), RoundedCornerShape(8.dp))
            .border(1.dp, Color(0xFF37474F), RoundedCornerShape(8.dp))
            .padding(8.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, color = Color.LightGray, fontSize = 13.sp)
        Text(value, color = Color(0xFF81C784), fontSize = 13.sp)
    }
}
