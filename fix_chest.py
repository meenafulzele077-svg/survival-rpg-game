with open("app/src/main/java/com/example/ui/SpriteRenderers.kt", "a") as f:
    f.write("""
// HD Treasure Chest
fun DrawScope.drawPixelChest(x: Float, y: Float) {
    drawOval(Color(0x66000000), Offset(x - 22f, y + 10f), Size(44f, 18f))
    // Chest wooden box
    drawRoundRect(Color(0xFF6D4C41), Offset(x - 20f, y - 16f), Size(40f, 32f), CornerRadius(5f, 5f))
    // Gold straps and lock
    drawRect(Color(0xFFFFD54F), Offset(x - 14f, y - 16f), Size(4f, 32f))
    drawRect(Color(0xFFFFD54F), Offset(x + 10f, y - 16f), Size(4f, 32f))
    drawCircle(Color(0xFFFFD54F), 5f, Offset(x, y - 2f))
    drawCircle(Color(0xFF212121), 2f, Offset(x, y - 2f))
}
""")
print("Added drawPixelChest successfully!")
