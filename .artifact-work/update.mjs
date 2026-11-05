import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load('Manual_Test_Scripts.xlsx'));
const sheet=wb.worksheets.getItem('TC-007 Wishlist to Cart');
const savePreview=async(name,range)=>{const p=await wb.render({sheetName:sheet.name,range,scale:1,format:'png'});await fs.writeFile(`.artifact-work/${name}.png`,new Uint8Array(await p.arrayBuffer()));};
if(process.argv.includes('--preview')) {console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:2500})).ndjson);await savePreview('before','A10:C15');process.exit(0);}
sheet.getRange('B2').values=[['tests/wishlistToCart.spec.js']];
sheet.getRange('B4').values=[['Start signed out. Register a fresh account with a unique email, then sign in. Cart and wishlist must be empty; the selected book must be available.']];
sheet.getRange('B5').values=[['Name: Workflow Tester; email: workflow-<unique ID>@example.com; contact: 1234567890; password: 1234. Product: The Wimpy Kid Do -It- Yourself Book; cart quantity: 1.']];
sheet.getRange('B6').values=[['Coverage: Integration. Compare the current selling price, excluding the old price. Account remains registered. Manually remove cart/wishlist data: current automation cleanup is skipped because local variables shadow hook variables. Session teardown signs out.']];
sheet.getRange('B11:C15').values=[
['Register the fresh account, accept confirmation and sign in. Open Books and the selected book. Add it to Wishlist.','Registration confirms success; Logout is visible. Product heading matches the selected book and exactly one matching wishlist row is present.'],
['Record the wishlist current selling price P, excluding the old price. Click Add to cart on that row, accept any confirmation and open My Cart.','Exactly one matching cart row and one quantity field are present; quantity is 1. Cart unit price is positive and equals P.'],
['Record cart unit price, shipping, row total and grand total. Compare the displayed amounts.','Row total equals (1 x unit price) + shipping, within 0.01. Grand total equals the row total within 0.01.'],
['Reload My Cart. Recheck the product row, quantity, positive unit price and totals. Open the cart product link.','One matching row and one quantity field remain; quantity is 1 and totals still reconcile. The product link opens details with the exact selected book heading.'],
['Return to My Cart; fill required billing/shipping address fields, select the test item for removal and click Update shopping cart. Remove its wishlist entry if present, reload Wishlist, then log out.','The cart displays Your shopping Cart is empty; no matching wishlist row remains. Session is signed out. Perform cleanup manually even if earlier steps fail.']
];
wb.worksheets.getItem('Read Me').getRange('C14').values=[['tests/wishlistToCart.spec.js']];
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:"'TC-007 Wishlist to Cart'!B11:C15",tableMaxRows:5,tableMaxCols:2,maxChars:5000})).ndjson);
await savePreview('after','A10:C15');
const out=await SpreadsheetFile.exportXlsx(wb);await out.save('outputs/manual-test-update/Manual_Test_Scripts.xlsx');
