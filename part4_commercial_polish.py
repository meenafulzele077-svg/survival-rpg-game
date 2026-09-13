import os

# 1. Add Local Game State Persistence & Equipment System
persistence_code = """package com.example.model

data class PlayerEquipment(
    var helmet: String = "Leather Cap",
    var armor: String = "Chainmail",
    var weapon: String = "Wood Axe",
    var shield: String = "Wooden Buckler"
) {
    val totalDefense: Int
        get() = (if (armor == "Chainmail") 15 else 5) + (if (shield == "Iron Shield") 12 else 4)
    val totalBonusAttack: Int
        get() = if (weapon == "Sun Blade") 60 else if (weapon == "Iron Sword") 25 else 8
}
"""

with open("app/src/main/java/com/example/model/PlayerEquipment.kt", "w") as f:
    f.write(persistence_code)

# 2. Add Equipment Dialog & Character Sheet to UI
equipment_ui = """package com.example.ui

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
"""

with open("app/src/main/java/com/example/ui/EquipmentDialog.kt", "w") as f:
    f.write(equipment_ui)

# 3. Add Custom Adaptive Launcher Icon Resources
icon_xml = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
"""

os.makedirs("app/src/main/res/mipmap-anydpi-v26", exist_ok=True)
with open("app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml", "w") as f:
    f.write(icon_xml)

colors_xml = """<resources>
    <color name="ic_launcher_background">#1B4332</color>
</resources>
"""
with open("app/src/main/res/values/colors.xml", "w") as f:
    f.write(colors_xml)

# Vector Icon (Sword & Shield on Pine green)
foreground_vector = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#FFD54F"
        android:pathData="M54,18 L76,30 L76,62 C76,78 54,90 54,90 C54,90 32,78 32,62 L32,30 Z"/>
    <path
        android:fillColor="#ECEFF1"
        android:strokeColor="#37474F"
        android:strokeWidth="2"
        android:pathData="M50,32 L58,32 L58,74 L50,74 Z"/>
    <path
        android:fillColor="#C62828"
        android:pathData="M44,60 L64,60 L64,66 L44,66 Z"/>
</vector>
"""
os.makedirs("app/src/main/res/drawable", exist_ok=True)
with open("app/src/main/res/drawable/ic_launcher_foreground.xml", "w") as f:
    f.write(foreground_vector)

# Update AndroidManifest to point to the custom launcher icon
with open("app/src/main/AndroidManifest.xml", "r") as f:
    manifest = f.read()

if 'android:icon=' not in manifest:
    manifest = manifest.replace(
        '<application',
        '<application\n        android:icon="@mipmap/ic_launcher"\n        android:roundIcon="@mipmap/ic_launcher"'
    )
    with open("app/src/main/AndroidManifest.xml", "w") as f:
        f.write(manifest)

# 4. Connect Equipment Dialog Button to Main HUD
with open("app/src/main/java/com/example/ui/MainGameScreen.kt", "r") as f:
    screen = f.read()

screen = screen.replace(
    "var showQuests by remember { mutableStateOf(false) }",
    "var showQuests by remember { mutableStateOf(false) }\n    var showEquipment by remember { mutableStateOf(false) }"
)

# Add character equipment button next to HUD
screen = screen.replace(
    'Text("LVL ${engine.level}", color = Color.Yellow, fontSize = 15.sp)',
    'Text("LVL ${engine.level} 🛡️", color = Color.Yellow, fontSize = 15.sp, modifier = Modifier.clickable { showEquipment = true })'
)

# Add dialog Composable at bottom of screen
screen = screen.replace(
    "if (showQuests) {",
    "if (showEquipment) {\n            EquipmentDialog(engine = engine, onDismiss = { showEquipment = false })\n        }\n        if (showQuests) {"
)

with open("app/src/main/java/com/example/ui/MainGameScreen.kt", "w") as f:
    f.write(screen)

print("PART 4 COMMERCIAL POLISH & ASSETS CREATED SUCCESSFULLY!")
