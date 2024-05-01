<script lang="ts">
	import { Progress } from 'stwui';
</script>

<section class="flex h-screen flex-col items-center justify-center">
	<h1 class="m-2 text-2xl">{'Unity Auth'}</h1>
	<p class="m-2 text-base font-normal">{'Loading...'}</p>
	<div class="m-2 w-52 max-w-52">
		<Progress value={0} indeterminate size="md" />
	</div>
</section>

<style>
	section {
		background-color: hsl(var(--background));
	}
</style>
