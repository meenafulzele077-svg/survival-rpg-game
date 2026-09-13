import os

files = {
    "app/src/main/java/com/example/audio/SoundFX.kt": """package com.example.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import kotlin.concurrent.thread
import kotlin.math.*

class SoundFX(context: Context) {
    private val vibrator: Vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        val vm = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
        vm.defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
    }

    // Procedural 8-bit / 16-bit Sound Synthesizer
    fun playSound(type: String) {
        thread(start = true) {
            try {
                val sampleRate = 22050
                val (durationMs, startFreq, endFreq) = when (type) {
                    "CHOP" -> Triple(80, 220.0, 90.0)      // Low wood impact thud
                    "MINE" -> Triple(70, 880.0, 1200.0)    // High metal clink
                    "HIT" -> Triple(120, 350.0, 110.0)     // Flesh punch / sword hit
                    "SLASH" -> Triple(90, 600.0, 200.0)    // Whoosh sword swing
                    "COIN" -> Triple(100, 987.0, 1318.0)   // High crystal coin ding
                    else -> Triple(60, 440.0, 440.0)
                }

                val numSamples = (sampleRate * durationMs / 1000)
                val buffer = ShortArray(numSamples)
                for (i in 0 until numSamples) {
                    val progress = i.toDouble() / numSamples
                    val freq = startFreq + (endFreq - startFreq) * progress
                    val wave = sin(2.0 * PI * i * freq / sampleRate)
                    val envelope = 1.0 - progress // Linear fade-out
                    buffer[i] = (wave * envelope * Short.MAX_VALUE * 0.45).toInt().toShort()
                }

                val audioTrack = AudioTrack.Builder()
                    .setAudioAttributes(
                        AudioAttributes.Builder()
                            .setUsage(AudioAttributes.USAGE_GAME)
                            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                            .build()
                    )
                    .setAudioFormat(
                        AudioFormat.Builder()
                            .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                            .setSampleRate(sampleRate)
                            .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                            .build()
                    )
                    .setBufferSizeInBytes(buffer.size * 2)
                    .setTransferMode(AudioTrack.MODE_STATIC)
                    .build()

                audioTrack.write(buffer, 0, buffer.size)
                audioTrack.play()
                Thread.sleep(durationMs.toLong() + 20)
                audioTrack.release()
            } catch (_: Exception) {}
        }
    }

    fun vibrate(durationMs: Long = 35) {
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createOneShot(durationMs, VibrationEffect.DEFAULT_AMPLITUDE))
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(durationMs)
            }
        } catch (_: Exception) {}
    }
}
""",

    "app/src/main/java/com/example/model/DamagePopup.kt": """package com.example.model

data class DamagePopup(
    val id: Long,
    val text: String,
    val x: Float,
    var y: Float,
    val colorHex: Long,
    var alpha: Float = 1.0f
)
""",

    "app/src/main/java/com/example/ui/MiniMap.kt": """package com.example.ui

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
"""
}

for path, content in files.items():
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"Generated: {path}")

print("✅ Part 2 Systems Built!")
