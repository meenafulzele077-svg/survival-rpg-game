package com.example.audio

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
