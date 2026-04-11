package com.ulak

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.switchmaterial.SwitchMaterial
import com.google.android.material.textfield.TextInputEditText

class SettingsActivity : AppCompatActivity() {
    
    private lateinit var deviceNameInput: TextInputEditText
    private lateinit var encryptionSwitch: SwitchMaterial
    private lateinit var notificationSwitch: SwitchMaterial
    private lateinit var wifiDirectSwitch: SwitchMaterial
    private lateinit var encryptionPasswordInput: TextInputEditText
    private lateinit var encryptionPasswordLayout: com.google.android.material.textfield.TextInputLayout
    private lateinit var encryptionPasswordLabel: com.google.android.material.textview.MaterialTextView
    private lateinit var encryptionPasswordNote: com.google.android.material.textview.MaterialTextView
    private lateinit var autoAcceptSwitch: SwitchMaterial
    private lateinit var aboutButton: MaterialButton
    private lateinit var downloadDesktopButton: MaterialButton
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)
        
        setupViews()
        loadSettings()
        setupBottomNavigation()
        
        // Intent'ten gelen odaklanma isteklerini işle
        if (intent.getBooleanExtra("focus_device_name", false)) {
            deviceNameInput.requestFocus()
            val imm = getSystemService(android.content.Context.INPUT_METHOD_SERVICE) as android.view.inputmethod.InputMethodManager
            imm.showSoftInput(deviceNameInput, android.view.inputmethod.InputMethodManager.SHOW_IMPLICIT)
        }
        
        if (intent.getBooleanExtra("focus_encryption", false)) {
            encryptionSwitch.requestFocus()
            // Scroll to encryption switch
            findViewById<android.widget.ScrollView>(R.id.settingsScrollView)?.post {
                findViewById<android.widget.ScrollView>(R.id.settingsScrollView)?.smoothScrollTo(0, encryptionSwitch.top)
            }
        }
    }
    
    private fun setupViews() {
        deviceNameInput = findViewById(R.id.deviceNameInput)
        encryptionSwitch = findViewById(R.id.encryptionSwitch)
        notificationSwitch = findViewById(R.id.notificationSwitch)
        wifiDirectSwitch = findViewById(R.id.wifiDirectSwitch)
        encryptionPasswordInput = findViewById(R.id.encryptionPasswordInput)
        encryptionPasswordLayout = findViewById(R.id.encryptionPasswordLayout)
        encryptionPasswordLabel = findViewById(R.id.encryptionPasswordLabel)
        encryptionPasswordNote = findViewById(R.id.encryptionPasswordNote)
        autoAcceptSwitch = findViewById(R.id.autoAcceptSwitch)
        aboutButton = findViewById(R.id.aboutButton)
        downloadDesktopButton = findViewById(R.id.downloadDesktopButton)
        
        val networkManagerInstance = NetworkManager.getInstance(this)
        deviceNameInput.setText(networkManagerInstance.deviceName)
        
        encryptionSwitch.setOnCheckedChangeListener { _, isChecked ->
            updatePasswordVisibility(isChecked)
        }
        
        wifiDirectSwitch.setOnCheckedChangeListener { _, isChecked ->
            val prefs = getSharedPreferences("ulak_prefs", MODE_PRIVATE)
            prefs.edit().putBoolean("wifi_direct_enabled", isChecked).apply()
            
            val netMgr = NetworkManager.getInstance(this)
            val localIp = netMgr.getLocalIp()
            val isP2P = netMgr.isWifiDirectActive()
            
            android.widget.Toast.makeText(
                this,
                if (isChecked) {
                    "Wi-Fi Direct etkinleştirildi\n\nYerel IP: $localIp\nP2P Aktif: $isP2P\n\n⚠️ Her iki cihazda da açık olmalı!"
                } else {
                    "Wi-Fi Direct devre dışı"
                },
                android.widget.Toast.LENGTH_LONG
            ).show()
        }
        
        aboutButton.setOnClickListener {
            startActivity(Intent(this, AboutActivity::class.java))
        }
        
        downloadDesktopButton.setOnClickListener {
            val intent = Intent(Intent.ACTION_VIEW, android.net.Uri.parse("https://ulak.algsoft.net.tr/"))
            startActivity(intent)
        }
    }
    
    private fun loadSettings() {
        val prefs = getSharedPreferences("ulak_prefs", MODE_PRIVATE)
        encryptionSwitch.isChecked = prefs.getBoolean("use_encryption", false)
        notificationSwitch.isChecked = prefs.getBoolean("use_notifications", true)
        wifiDirectSwitch.isChecked = prefs.getBoolean("wifi_direct_enabled", false)
        autoAcceptSwitch.isChecked = prefs.getBoolean("auto_accept", false)
        encryptionPasswordInput.setText(prefs.getString("encryption_password", ""))
        updatePasswordVisibility(encryptionSwitch.isChecked)
    }
    
    private fun saveSettings() {
        val prefs = getSharedPreferences("ulak_prefs", MODE_PRIVATE)
        prefs.edit().apply {
            putString("device_name", deviceNameInput.text.toString())
            putBoolean("use_encryption", encryptionSwitch.isChecked)
            putBoolean("use_notifications", notificationSwitch.isChecked)
            putBoolean("wifi_direct_enabled", wifiDirectSwitch.isChecked)
            putBoolean("auto_accept", autoAcceptSwitch.isChecked)
            putString("encryption_password", encryptionPasswordInput.text.toString())
            apply()
        }
        
        val networkManager = NetworkManager.getInstance(this)
        networkManager.setDeviceName(deviceNameInput.text.toString())
        networkManager.updateEncryptionKey(encryptionPasswordInput.text.toString())
    }
    
    override fun onPause() {
        super.onPause()
        saveSettings()
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
    
    private fun setupBottomNavigation() {
        findViewById<com.google.android.material.bottomnavigation.BottomNavigationView>(R.id.bottomNavigation).apply {
            selectedItemId = R.id.nav_settings
            setOnItemSelectedListener { item ->
                when (item.itemId) {
                    R.id.nav_send -> {
                        startActivity(Intent(this@SettingsActivity, MainActivity::class.java))
                        finish()
                        true
                    }
                    R.id.nav_receive -> {
                        startActivity(Intent(this@SettingsActivity, ReceiveActivity::class.java))
                        finish()
                        true
                    }
                    R.id.nav_settings -> true
                    else -> false
                }
            }
        }
    }
    
    private fun updatePasswordVisibility(isEncryptionEnabled: Boolean) {
        val visibility = if (isEncryptionEnabled) android.view.View.VISIBLE else android.view.View.GONE
        encryptionPasswordLabel.visibility = visibility
        encryptionPasswordLayout.visibility = visibility
        encryptionPasswordNote.visibility = visibility
    }
}
