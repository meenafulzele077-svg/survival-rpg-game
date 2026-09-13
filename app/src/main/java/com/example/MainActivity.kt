package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import com.example.audio.SoundFX
import com.example.engine.GameEngine
import com.example.ui.MainGameScreen

class MainActivity : ComponentActivity() {
    private lateinit var soundFx: SoundFX
    private lateinit var engine: GameEngine

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        soundFx = SoundFX(this)
        engine = GameEngine(soundFx)

        setContent {
            MaterialTheme(colorScheme = darkColorScheme()) {
                Surface(modifier = Modifier.fillMaxSize(), color = Color(0xFF0F1416)) {
                    MainGameScreen(engine = engine)
                }
            }
        }
    }
}
