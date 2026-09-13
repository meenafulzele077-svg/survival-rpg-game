# 1. Update MiniMap.kt to use rawPlayerX / rawPlayerY
minimap_code = """package com.example.ui

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
"""

with open("app/src/main/java/com/example/ui/MiniMap.kt", "w") as f:
    f.write(minimap_code)

# 2. Append CraftingDialog and QuestDialog to MainGameScreen.kt so they are never missing
with open("app/src/main/java/com/example/ui/MainGameScreen.kt", "a") as f:
    f.write("""

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
""")

print("Cleaned up MiniMap, CraftingDialog and QuestDialog!")
