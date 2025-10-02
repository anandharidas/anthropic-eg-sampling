import { NextRequest, NextResponse } from 'next/server'
import { spawn } from 'child_process'

export async function POST(req: NextRequest) {
  try {
    const { url } = await req.json()
    if (typeof url !== 'string' || !url.startsWith('http')) {
      return NextResponse.json({ error: 'Invalid url' }, { status: 400 })
    }

    // Spawn the python client in printable mode and feed the URL via stdin prompts.
    // We rely on the interactive menu: send "printable_summary" then the url, then "quit".
    const proc = spawn('uv', ['run', 'client.py'], {
      cwd: process.cwd().replace(/\/web$/, ''),
      env: process.env,
    })

    let stdout = ''
    let stderr = ''

    proc.stdout.on('data', (d) => {
      stdout += d.toString()
      // Heuristics: once menu appears, send action and URL
      if (stdout.includes('Enter action')) {
        proc.stdin.write('printable_summary\n')
      }
      if (stdout.includes('Enter the HTTP link')) {
        proc.stdin.write(url + '\n')
      }
      if (stdout.includes('Markdown Formatted Summary:')) {
        // We'll let the process continue; the caller will parse the block
      }
    })

    proc.stderr.on('data', (d) => {
      stderr += d.toString()
    })

    const result: string = await new Promise((resolve, reject) => {
      proc.on('close', () => {
        // Extract the markdown section printed by the client
        const marker = 'Markdown Formatted Summary:\n'
        const idx = stdout.indexOf(marker)
        if (idx >= 0) {
          const md = stdout.substring(idx + marker.length).trim()
          resolve(md)
        } else if (stderr) {
          reject(new Error(stderr))
        } else {
          reject(new Error('No markdown output detected.'))
        }
      })
      proc.on('error', reject)
    })

    return NextResponse.json({ markdown: result })
  } catch (e: any) {
    return NextResponse.json({ error: e.message || String(e) }, { status: 500 })
  }
}


