package com.ulak

import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textview.MaterialTextView
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

data class ReceivedItem(val timestamp: Long, val name: String, val sender: String)

class ReceiveActivity : AppCompatActivity() {
    
    private lateinit var historyRecyclerView: RecyclerView
    private lateinit var historyCountText: MaterialTextView
    private lateinit var clearButton: MaterialButton
    private lateinit var openFolderButton: MaterialButton
    private lateinit var itemsAdapter: ReceivedItemsAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_receive)
        
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        
        setupViews()
        loadReceivedItems()
        setupBottomNavigation()
        
        if (intent.getBooleanExtra("show_text_dialog", false)) {
            val text = intent.getStringExtra("text_content") ?: ""
            val sender = intent.getStringExtra("text_sender") ?: "Unknown"
            android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                showTextReceivedDialog(text, sender)
            }, 300)
        }
        
        TransferRequestHolder.pendingRequest?.let { request ->
            android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                showTransferRequestDialog(request.filename, request.filesize, request.sender, request.callback)
                TransferRequestHolder.pendingRequest = null
            }, 300)
        }
    }
    
    override fun onResume() {
        super.onResume()
        loadReceivedItems()
    }
    
    private fun setupViews() {
        historyRecyclerView = findViewById(R.id.historyRecyclerView)
        historyCountText = findViewById(R.id.historyCountText)
        clearButton = findViewById(R.id.clearButton)
        openFolderButton = findViewById(R.id.openFolderButton)
        
        itemsAdapter = ReceivedItemsAdapter()
        historyRecyclerView.layoutManager = LinearLayoutManager(this)
        historyRecyclerView.adapter = itemsAdapter
        
        clearButton.setOnClickListener {
            clearReceivedList()
        }
        
        openFolderButton.setOnClickListener {
            openDownloadsFolder()
        }
    }
    
    private fun loadReceivedItems() {
        val prefs = getSharedPreferences("ulak_received", Context.MODE_PRIVATE)
        val itemsSet = prefs.getStringSet("items", emptySet()) ?: emptySet()
        
        val items = itemsSet.mapNotNull { str ->
            val parts = str.split("|")
            if (parts.size == 3) {
                ReceivedItem(parts[0].toLong(), parts[1], parts[2])
            } else null
        }.sortedByDescending { it.timestamp }
        
        historyCountText.text = "${items.size} alındı"
        itemsAdapter.updateItems(items)
    }
    
    private fun clearReceivedList() {
        AlertDialog.Builder(this, R.style.ULAKDialogTheme)
            .setTitle("Listeyi Temizle")
            .setMessage("Alınanlar listesi temizlenecek. Dosyalar silinmeyecek. Devam edilsin mi?")
            .setPositiveButton("Evet") { _, _ ->
                val prefs = getSharedPreferences("ulak_received", Context.MODE_PRIVATE)
                prefs.edit().remove("items").apply()
                loadReceivedItems()
            }
            .setNegativeButton("İptal", null)
            .show()
            .window?.setBackgroundDrawableResource(R.drawable.dialog_background)
    }
    
    private fun openDownloadsFolder() {
        try {
            val intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(Uri.parse(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).path), "resource/folder")
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            startActivity(intent)
        } catch (e: Exception) {
            val intent = Intent(Intent.ACTION_VIEW)
            val uri = Uri.parse("content://com.android.externalstorage.documents/document/primary:Download")
            intent.setDataAndType(uri, "vnd.android.document/directory")
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            try {
                startActivity(intent)
            } catch (e: Exception) {
                Toast.makeText(this, "Dosya yöneticisi açılamadı", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun showTextReceivedDialog(text: String, sender: String) {
        val input = TextInputEditText(this)
        input.setText(text)
        input.isFocusable = false
        input.isClickable = false
        input.setTextIsSelectable(true)
        input.setTextColor(androidx.core.content.ContextCompat.getColor(this, R.color.text_primary))
        
        AlertDialog.Builder(this, R.style.ULAKDialogTheme)
            .setTitle("$sender - Metin Gönderdi")
            .setView(input)
            .setPositiveButton("Kopyala") { _, _ ->
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clip = android.content.ClipData.newPlainText("Metin", text)
                clipboard.setPrimaryClip(clip)
                Toast.makeText(this, "Metin kopyalandı", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Kapat", null)
            .show()
            .window?.setBackgroundDrawableResource(R.drawable.dialog_background)
    }
    
    private fun showSavedText(timestamp: Long, sender: String) {
        val prefs = getSharedPreferences("ulak_texts", Context.MODE_PRIVATE)
        val data = prefs.getString(timestamp.toString(), null)
        
        if (data == null) {
            Toast.makeText(this, "Metin içeriği bulunamadı", Toast.LENGTH_SHORT).show()
            return
        }
        
        val parts = data.split("|", limit = 2)
        val text = if (parts.size == 2) parts[1] else data
        
        val input = TextInputEditText(this)
        input.setText(text)
        input.isFocusable = false
        input.isClickable = false
        input.setTextIsSelectable(true)
        input.setTextColor(androidx.core.content.ContextCompat.getColor(this, R.color.text_primary))
        
        AlertDialog.Builder(this, R.style.ULAKDialogTheme)
            .setTitle("$sender - Metin")
            .setView(input)
            .setPositiveButton("Kopyala") { _, _ ->
                val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clip = android.content.ClipData.newPlainText("Metin", text)
                clipboard.setPrimaryClip(clip)
                Toast.makeText(this, "Metin kopyalandı", Toast.LENGTH_SHORT).show()
            }
            .setNegativeButton("Kapat", null)
            .show()
            .window?.setBackgroundDrawableResource(R.drawable.dialog_background)
    }
    
    private fun showTransferRequestDialog(filename: String, filesize: Long, sender: String, callback: (Boolean) -> Unit) {
        val sizeKB = filesize / 1024
        val extension = filename.substringAfterLast('.', "")
        val type = when (extension.lowercase()) {
            "jpg", "jpeg", "png", "gif" -> "Resim"
            "mp4", "avi", "mkv" -> "Video"
            "mp3", "wav" -> "Ses"
            "pdf" -> "PDF"
            "apk" -> "Uygulama"
            "txt" -> "Metin"
            "zip" -> "Arşiv"
            else -> "Dosya"
        }
        
        val message = "Gönderen: $sender\n\nDosya: $filename\nTür: $type\nBoyut: $sizeKB KB\n\nKabul ediyor musunuz?"
        
        AlertDialog.Builder(this, R.style.ULAKDialogTheme)
            .setTitle("Dosya Alınıyor")
            .setMessage(message)
            .setPositiveButton("Kabul Et") { _, _ ->
                callback(true)
            }
            .setNegativeButton("Reddet") { _, _ ->
                callback(false)
            }
            .setCancelable(false)
            .show()
            .window?.setBackgroundDrawableResource(R.drawable.dialog_background)
    }
    
    private inner class ReceivedItemsAdapter : 
        RecyclerView.Adapter<ReceivedItemsAdapter.ItemViewHolder>() {
        
        private var items = listOf<ReceivedItem>()
        
        fun updateItems(newItems: List<ReceivedItem>) {
            items = newItems
            notifyDataSetChanged()
        }
        
        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ItemViewHolder {
            val view = LayoutInflater.from(parent.context)
                .inflate(android.R.layout.simple_list_item_2, parent, false)
            return ItemViewHolder(view)
        }
        
        override fun onBindViewHolder(holder: ItemViewHolder, position: Int) {
            holder.bind(items[position])
        }
        
        override fun getItemCount() = items.size
        
        inner class ItemViewHolder(view: View) : RecyclerView.ViewHolder(view) {
            private val text1: MaterialTextView = view.findViewById(android.R.id.text1)
            private val text2: MaterialTextView = view.findViewById(android.R.id.text2)
            
            fun bind(item: ReceivedItem) {
                text1.text = item.name
                val dateFormat = SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.getDefault())
                text2.text = "${item.sender} - ${dateFormat.format(Date(item.timestamp))}"
                
                itemView.setOnClickListener {
                    if (item.name.startsWith("Metin:")) {
                        showSavedText(item.timestamp, item.sender)
                    } else {
                        openFile(item.name)
                    }
                }
            }
        }
    }
    
    private fun openFile(filename: String) {
        val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        val file = File(downloadsDir, filename)
        
        if (!file.exists()) {
            Toast.makeText(this, "Dosya bulunamadı", Toast.LENGTH_SHORT).show()
            return
        }
        
        try {
            val uri = FileProvider.getUriForFile(this, "${packageName}.provider", file)
            val intent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, getMimeType(file))
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(this, "Dosya açılamıyor: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun getMimeType(file: File): String {
        return when (file.extension.lowercase()) {
            "jpg", "jpeg", "png", "gif", "bmp", "webp" -> "image/*"
            "mp4", "avi", "mkv", "mov", "3gp", "webm" -> "video/*"
            "mp3", "wav", "ogg", "m4a", "flac", "aac" -> "audio/*"
            "pdf" -> "application/pdf"
            "apk" -> "application/vnd.android.package-archive"
            "txt", "log" -> "text/plain"
            "zip", "rar", "7z" -> "application/zip"
            "doc", "docx" -> "application/msword"
            "xls", "xlsx" -> "application/vnd.ms-excel"
            "ppt", "pptx" -> "application/vnd.ms-powerpoint"
            else -> "*/*"
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
    
    private fun setupBottomNavigation() {
        findViewById<com.google.android.material.bottomnavigation.BottomNavigationView>(R.id.bottomNavigation).apply {
            selectedItemId = R.id.nav_receive
            setOnItemSelectedListener { item ->
                when (item.itemId) {
                    R.id.nav_send -> {
                        startActivity(Intent(this@ReceiveActivity, MainActivity::class.java))
                        finish()
                        true
                    }
                    R.id.nav_receive -> true
                    R.id.nav_settings -> {
                        startActivity(Intent(this@ReceiveActivity, SettingsActivity::class.java))
                        finish()
                        true
                    }
                    else -> false
                }
            }
        }
    }
}
