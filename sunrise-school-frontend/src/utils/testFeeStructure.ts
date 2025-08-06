// Test utility to demonstrate fee structure data retrieval and formatting
import { enhancedFeesAPI } from '../services/api';

interface FeeStructureData {
  id: number;
  class_id: number;
  session_year_id: number;
  class_name: string;
  session_year_name: string;
  tuition_fee: number;
  admission_fee: number;
  development_fee: number;
  activity_fee: number;
  transport_fee: number;
  library_fee: number;
  lab_fee: number;
  exam_fee: number;
  other_fee: number;
  total_annual_fee: number;
}

export const testFeeStructureRetrieval = async () => {
  try {
    console.log('🔍 Testing Fee Structure Data Retrieval...');
    
    // Fetch fee structure data
    const response = await enhancedFeesAPI.getFeeStructure();
    console.log('✅ Raw API Response:', response.data);
    
    // Filter for current session year (2025-26)
    const currentSessionStructures = response.data
      .filter((structure: FeeStructureData) => structure.session_year_name === '2025-26');
    
    console.log('📊 Current Session (2025-26) Structures:', currentSessionStructures);
    
    // Format data for display
    const formattedData = currentSessionStructures.map((structure: FeeStructureData) => ({
      class: structure.class_name,
      monthlyTuition: `₹${Math.round(structure.total_annual_fee / 12)?.toLocaleString() || '0'}`,
      annualTuition: `₹${structure.total_annual_fee?.toLocaleString() || '0'}`,
      components: {
        tuition: structure.tuition_fee,
        development: structure.development_fee,
        activity: structure.activity_fee,
        transport: structure.transport_fee,
        library: structure.library_fee,
        lab: structure.lab_fee,
        exam: structure.exam_fee,
        other: structure.other_fee
      },
      note: 'Only tuition fees apply - all other fees are ₹0'
    }));
    
    console.log('💰 Formatted Fee Structure Data:');
    console.table(formattedData);
    
    return formattedData;
    
  } catch (error) {
    console.error('❌ Error testing fee structure retrieval:', error);
    throw error;
  }
};

export const displayFeeStructureSummary = (structures: FeeStructureData[]) => {
  console.log('\n📋 FEE STRUCTURE SUMMARY - SUNRISE NATIONAL PUBLIC SCHOOL');
  console.log('=' .repeat(80));
  console.log('Academic Session: 2025-26');
  console.log('Grade Levels: Pre-Kindergarten through Grade 8');
  console.log('=' .repeat(80));
  
  structures.forEach((structure, index) => {
    console.log(`\n${index + 1}. ${structure.class_name.toUpperCase()}`);
    console.log('-'.repeat(40));
    console.log(`   Monthly Tuition:   ₹${Math.round(structure.total_annual_fee / 12).toLocaleString()}`);
    console.log(`   Annual Tuition:    ₹${structure.total_annual_fee.toLocaleString()}`);
    console.log(`   Admission Fee:     ₹0 (No admission fees)`);

    // Show fee components if they exist (currently only tuition_fee has values)
    const components = [
      { name: 'Tuition', amount: structure.tuition_fee },
      { name: 'Development', amount: structure.development_fee },
      { name: 'Activity', amount: structure.activity_fee },
      { name: 'Transport', amount: structure.transport_fee },
      { name: 'Library', amount: structure.library_fee },
      { name: 'Lab', amount: structure.lab_fee },
      { name: 'Exam', amount: structure.exam_fee },
      { name: 'Other', amount: structure.other_fee }
    ].filter(comp => comp.amount > 0);

    if (components.length > 0) {
      console.log('   Fee Components:');
      components.forEach(comp => {
        console.log(`     - ${comp.name}: ₹${comp.amount.toLocaleString()}`);
      });
    } else {
      console.log('   Note: Only tuition fees apply - all other components are ₹0');
    }
  });
  
  console.log('\n' + '='.repeat(80));
  console.log('Note: Monthly tuition calculated by dividing annual tuition by 12 months');
  console.log('Current fee structure: Only tuition fees apply - no admission or other fees');
  console.log('Additional charges may apply for uniforms, books, transport, and optional services');
  console.log('='.repeat(80));
};

// Usage example:
// testFeeStructureRetrieval().then(data => displayFeeStructureSummary(data));
