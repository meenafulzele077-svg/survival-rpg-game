import os

files = {
    "settings.gradle.kts": """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "Survival RPG"
include(":app")
""",

    "build.gradle.kts": """plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "2.0.0" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.0" apply false
}
""",

    "app/build.gradle.kts": """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.example"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.aistudio.survivalrpg.mkwpza"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.4")
    implementation("androidx.activity:activity-compose:1.9.1")
    implementation(platform("androidx.compose:compose-bom:2024.06.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
}
""",

    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.VIBRATE" />
    <application
        android:allowBackup="true"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""",

    "app/src/main/res/values/strings.xml": """<resources>
    <string name="app_name">Survival RPG</string>
</resources>
""",

    "app/src/main/java/com/example/MainActivity.kt": """package com.example

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
""",

    ".github/workflows/build.yml": """name: Build Android APK

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v4

      - name: Generate Wrapper and Build APK
        run: |
          gradle wrapper --gradle-version 8.7
          chmod +x ./gradlew
          ./gradlew assembleDebug --no-daemon

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: app-debug-apk
          path: app/build/outputs/apk/debug/*.apk
"""
}

for path, content in files.items():
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"Created: {path}")

print("ALL FILES CLEANLY CREATED!")
