package com.ulak

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class AboutActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_about)

        findViewById<TextView>(R.id.tvVersion).text = "Versiyon ${BuildConfig.VERSION_NAME} - Android"

        mapOf(
            R.id.tvAlgsoftUrl to "https://algsoft.net.tr",
            R.id.tvFatihUrl to "https://fatihonder.org.tr",
            R.id.tvWebsiteUrl to "https://ulak.algsoft.net.tr",
            R.id.tvGithubUrl to "https://github.com/cektor/ULAK"
        ).forEach { (id, url) ->
            findViewById<TextView>(id).setOnClickListener { openUrl(url) }
        }
    }

    private fun openUrl(url: String) {
        startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
