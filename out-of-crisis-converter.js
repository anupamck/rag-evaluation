import { parseEpub } from '@gxl/epub-parser'
import { JSDOM } from 'jsdom'

// Function to extract clean text from HTML
function extractTextFromHTML(htmlString) {
  const dom = new JSDOM(htmlString)
  const document = dom.window.document
  
  // Remove script and style elements
  const scripts = document.querySelectorAll('script, style')
  scripts.forEach(el => el.remove())
  
  // Get text content and clean it up
  let text = document.body.textContent || document.body.innerText || ''
  
  // Clean up whitespace
  text = text
    .replace(/\s+/g, ' ')  // Replace multiple whitespace with single space
    .replace(/\n\s*\n/g, '\n')  // Clean up multiple newlines
    .trim()
  
  return text
}

const epubObj = await parseEpub('1.epub', {
  type: 'path',
})

// Sections to skip
const sectionsToSkip = [
  'Cover',
  'Contents', 
  'Foreword',
  'About the Author',
  'Preface',
  'Acknowledgments',
  'Appendix: Transformation in Japan',
  'Index'
]

// Filter out sections to skip
const filteredStructure = epubObj.structure.filter(section => 
  !sectionsToSkip.includes(section.name)
)

// Log the structure without content
console.log('=== EPUB STRUCTURE (Filtered) ===')
console.log('Filtered Structure (TOC):', filteredStructure)
console.log('\n=== SECTIONS INFO ===')
console.log('Total sections:', epubObj.sections.length)
console.log('Filtered sections:', filteredStructure.length)
console.log('Skipped sections:', sectionsToSkip)

// Log first section as example (without full HTML content)
if (epubObj.sections.length > 0) {
  console.log('\n=== FIRST SECTION EXAMPLE ===')
  console.log('ID:', epubObj.sections[0].id)
  console.log('HTML length:', epubObj.sections[0].htmlString.length, 'characters')
  console.log('HTML preview (first 200 chars):', epubObj.sections[0].htmlString.substring(0, 200) + '...')
}

// Function to extract subsections from HTML
function extractSubsections(htmlString) {
  const dom = new JSDOM(htmlString)
  const document = dom.window.document
  
  const sections = {}
  
  // Find all h2 and h3 elements (section headers)
  const headers = document.querySelectorAll('h2, h3')
  
  let currentSection = 'Introduction'
  let currentContent = []
  
  // Process all elements in the document
  const allElements = document.querySelectorAll('*')
  
  for (let i = 0; i < allElements.length; i++) {
    const element = allElements[i]
    
    // Check if this is a header
    if (element.tagName === 'H2' || element.tagName === 'H3') {
      // Save previous section if it has content
      if (currentContent.length > 0) {
        const content = currentContent.join(' ').trim()
        if (content.length > 0) {
          sections[currentSection] = content
        }
      }
      
      // Start new section
      currentSection = element.textContent.trim()
      currentContent = []
    } else {
      // Add text content to current section
      const text = element.textContent?.trim()
      if (text && text.length > 0) {
        currentContent.push(text)
      }
    }
  }
  
  // Add the last section
  if (currentContent.length > 0) {
    const content = currentContent.join(' ').trim()
    if (content.length > 0) {
      sections[currentSection] = content
    }
  }
  
  return sections
}

// Process all filtered chapters and create JSON
if (filteredStructure.length > 0) {
  console.log('\n=== PROCESSING ALL CHAPTERS FOR JSON ===')
  
  const jsonData = []
  
  for (let i = 0; i < filteredStructure.length; i++) {
    const chapter = filteredStructure[i]
    console.log(`Processing Chapter ${i + 1}: ${chapter.name}`)
    
    // Extract chapter number from the name (e.g., "1 Chain Reaction..." -> "1")
    const chapterNumber = chapter.name.match(/^(\d+)/)?.[1] || (i + 1).toString()
    const sectionId = `id_c${chapterNumber.padStart(3, '0')}`
    
    // Find the corresponding section
    const chapterSection = epubObj.sections.find(section => section.id === sectionId)
    
    if (chapterSection) {
      // Extract subsections
      const subsections = extractSubsections(chapterSection.htmlString)
      
      // Create chapter object
      const chapterObj = {
        url: `deming-book/chapter-${chapterNumber}`,
        title: chapter.name,
        sections: subsections
      }
      
      jsonData.push(chapterObj)
      console.log(`  ✓ Extracted ${Object.keys(subsections).length} subsections`)
    } else {
      console.log(`  ✗ Could not find section ${sectionId} for chapter ${chapterNumber}`)
    }
  }
  
  // Write JSON file
  const fs = await import('fs')
  const jsonString = JSON.stringify(jsonData, null, 2)
  fs.writeFileSync('out-of-crisis.json', jsonString)
  
  console.log(`\n=== JSON FILE CREATED ===`)
  console.log(`File: deming-book.json`)
  console.log(`Chapters processed: ${jsonData.length}`)
  console.log(`Total size: ${jsonString.length} characters`)
}
